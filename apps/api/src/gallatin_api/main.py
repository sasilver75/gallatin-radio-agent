from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gallatin_api.event_ledger import (
    AcceptedDomainEvent,
    CoaDecision,
    EventLedgerStore,
    EventEvidence,
    PostgresEventLedgerStore,
)
from gallatin_api.readiness import DependencyStatus, ReadinessResponse, check_postgis
from gallatin_api.radio import (
    FixtureTranscriptionPipeline,
    PostgresProposedInterpretationStore,
    PrerecordedRadioClipNotFound,
    ProposedInterpretationNotFound,
    ProposedInterpretationStore,
    PublicPrerecordedRadioClip,
    RadioTransmission,
    RadioTransmissionRequest,
    ReviewRequiredRadioInterpretation,
    TranscriptionPipeline,
    AddressedIntentRadioInterpretation,
    answer_addressed_intents,
    accepted_denied_area_event_for_interpretation,
    interpret_radio_transmission,
)
from gallatin_api.scenario import (
    ExecutableCourseOfAction,
    LogisticsPictureScenario,
    load_kaohsiung_tainan_logistics_picture,
    project_logistics_picture,
)
from gallatin_api.settings import Settings, get_settings

ReadinessChecker = Callable[[str], DependencyStatus]
ScenarioProvider = Callable[[], LogisticsPictureScenario]


def create_app(
    readiness_checker: ReadinessChecker | None = None,
    scenario_provider: ScenarioProvider | None = None,
    event_ledger_store: EventLedgerStore | None = None,
    proposed_interpretation_store: ProposedInterpretationStore | None = None,
    transcription_pipeline: TranscriptionPipeline | None = None,
) -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Gallatin Radio Agent API",
        version="0.1.0",
        description="API for the Quarterback demo workspace.",
    )
    checker = readiness_checker or check_postgis
    provide_scenario = scenario_provider or load_kaohsiung_tainan_logistics_picture
    ledger_store = event_ledger_store or PostgresEventLedgerStore(settings.database_url)
    proposed_store = proposed_interpretation_store or PostgresProposedInterpretationStore(
        settings.database_url
    )
    radio_transcription = transcription_pipeline or FixtureTranscriptionPipeline()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_web_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"service": "gallatin-radio-agent-api", "status": "ok"}

    @app.get(
        "/readyz",
        response_model=ReadinessResponse,
        responses={503: {"model": ReadinessResponse}},
    )
    def readyz(settings: Settings = Depends(get_settings)) -> JSONResponse:
        postgis = checker(settings.database_url)
        status = "ready" if postgis.status == "ready" else "unavailable"
        response = ReadinessResponse(
            service="gallatin-radio-agent-api",
            status=status,
            dependencies=[postgis],
        )
        status_code = 200 if status == "ready" else 503
        return JSONResponse(status_code=status_code, content=response.model_dump())

    @app.get(
        "/scenarios/kaohsiung-tainan/logistics-picture",
        response_model=LogisticsPictureScenario,
    )
    def kaohsiung_tainan_logistics_picture() -> LogisticsPictureScenario:
        return project_logistics_picture(provide_scenario(), ledger_store.list_events())

    @app.post(
        "/events/accepted",
        response_model=AcceptedDomainEvent,
        response_model_exclude_none=True,
        status_code=201,
    )
    def accept_event(event: AcceptedDomainEvent) -> AcceptedDomainEvent:
        return ledger_store.append(event)

    @app.get(
        "/events/accepted",
        response_model=list[AcceptedDomainEvent],
        response_model_exclude_none=True,
    )
    def accepted_events() -> list[AcceptedDomainEvent]:
        return ledger_store.list_events()

    @app.post(
        "/coas/{coa_id}/approve",
        response_model=AcceptedDomainEvent,
        response_model_exclude_none=True,
        status_code=201,
    )
    def approve_executable_coa(coa_id: str) -> AcceptedDomainEvent:
        picture = project_logistics_picture(provide_scenario(), ledger_store.list_events())
        event = coa_decision_event(picture, coa_id, "approved")
        return ledger_store.append(event)

    @app.post(
        "/coas/{coa_id}/reject",
        response_model=AcceptedDomainEvent,
        response_model_exclude_none=True,
        status_code=201,
    )
    def reject_executable_coa(coa_id: str) -> AcceptedDomainEvent:
        picture = project_logistics_picture(provide_scenario(), ledger_store.list_events())
        event = coa_decision_event(picture, coa_id, "rejected")
        return ledger_store.append(event)

    @app.get("/radio/prerecorded-clips", response_model=list[PublicPrerecordedRadioClip])
    def prerecorded_radio_clips() -> list[PublicPrerecordedRadioClip]:
        return radio_transcription.list_prerecorded_clips()

    @app.post(
        "/radio/transmissions",
        response_model=RadioTransmission,
        status_code=201,
    )
    def transmit_prerecorded_radio_clip(
        request: RadioTransmissionRequest,
    ) -> RadioTransmission:
        try:
            transmission = radio_transcription.transcribe_prerecorded_clip(request.clip_id)
        except PrerecordedRadioClipNotFound as exc:
            raise HTTPException(status_code=404, detail="Prerecorded Radio Clip not found") from exc

        interpreted = interpret_radio_transmission(transmission)
        for event in interpreted.accepted_events:
            ledger_store.append(event)
        for interpretation in interpreted.interpretations:
            if isinstance(interpretation, ReviewRequiredRadioInterpretation):
                proposed_store.upsert(interpretation)

        transmission = transmission.model_copy(update={"interpretations": interpreted.interpretations})
        if any(
            isinstance(interpretation, AddressedIntentRadioInterpretation)
            for interpretation in interpreted.interpretations
        ):
            transmission = answer_addressed_intents(
                transmission,
                project_logistics_picture(provide_scenario(), ledger_store.list_events()),
                proposed_store.list_interpretations(),
            )

        return transmission

    @app.post(
        "/interpretations/proposed/{interpretation_id}/accept",
        response_model=AcceptedDomainEvent,
        response_model_exclude_none=True,
        status_code=201,
    )
    def accept_proposed_interpretation(interpretation_id: str) -> AcceptedDomainEvent:
        try:
            interpretation = proposed_store.get(interpretation_id)
        except ProposedInterpretationNotFound as exc:
            raise HTTPException(
                status_code=404,
                detail="Proposed Interpretation not found",
            ) from exc

        if interpretation.status == "rejected":
            raise HTTPException(
                status_code=409,
                detail="Rejected Proposed Interpretation cannot be accepted",
            )

        event = accepted_denied_area_event_for_interpretation(interpretation)
        ledger_store.append(event)
        proposed_store.mark_accepted(interpretation_id, event.event_id)
        return event

    @app.post(
        "/interpretations/proposed/{interpretation_id}/reject",
        response_model=ReviewRequiredRadioInterpretation,
    )
    def reject_proposed_interpretation(interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        try:
            return proposed_store.mark_rejected(interpretation_id)
        except ProposedInterpretationNotFound as exc:
            raise HTTPException(
                status_code=404,
                detail="Proposed Interpretation not found",
            ) from exc

    @app.get(
        "/interpretations/proposed/{interpretation_id}",
        response_model=ReviewRequiredRadioInterpretation,
    )
    def proposed_interpretation(interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        try:
            return proposed_store.get(interpretation_id)
        except ProposedInterpretationNotFound as exc:
            raise HTTPException(
                status_code=404,
                detail="Proposed Interpretation not found",
            ) from exc

    return app


def coa_decision_event(
    picture: LogisticsPictureScenario,
    coa_id: str,
    decision: Literal["approved", "rejected"],
) -> AcceptedDomainEvent:
    coa = executable_coa_for_decision(picture, coa_id, decision)
    existing_decision_event = existing_coa_decision_event(picture, coa)
    if existing_decision_event is not None:
        return existing_decision_event

    movement = coa.movements[0] if coa.movements else None
    event_time = coa_decision_time(picture)
    decision_noun = "approval" if decision == "approved" else "rejection"
    selected_route_variant_id = movement.route_variant_id if decision == "approved" and movement else None
    selected_route_name = movement.route_name if decision == "approved" and movement else None
    movement_id = movement.movement_id if decision == "approved" and movement else None

    return AcceptedDomainEvent(
        event_id=f"evt-{coa_id}-{decision_noun}",
        event_type="coa_decision",
        subject_id=coa_id,
        source_callsign=picture.logistics_watch_officer,
        occurred_at=event_time,
        accepted_at=event_time,
        summary=f"{picture.logistics_watch_officer} {decision} {coa.name}.",
        evidence=[
            EventEvidence(
                kind="executable_coa",
                reference=coa_id,
            )
        ],
        coa_decision=CoaDecision(
            coa_id=coa_id,
            decision=decision,
            decided_by=picture.logistics_watch_officer,
            movement_id=movement_id,
            selected_route_variant_id=selected_route_variant_id,
            selected_route_name=selected_route_name,
        ),
    )


def existing_coa_decision_event(
    picture: LogisticsPictureScenario,
    coa: ExecutableCourseOfAction,
) -> AcceptedDomainEvent | None:
    if coa.decision_event_id is None:
        return None

    return next(
        (
            event
            for event in picture.event_ledger
            if event.event_id == coa.decision_event_id and event.event_type == "coa_decision"
        ),
        None,
    )


def executable_coa_for_decision(
    picture: LogisticsPictureScenario,
    coa_id: str,
    decision: Literal["approved", "rejected"],
) -> ExecutableCourseOfAction:
    coa = next((candidate for candidate in picture.executable_coas if candidate.coa_id == coa_id), None)
    if coa is None:
        raise HTTPException(status_code=404, detail="Executable COA not found")

    if coa.decision_status != "proposed" and coa.decision_status != decision:
        raise HTTPException(
            status_code=409,
            detail=f"Executable COA is already {coa.decision_status}",
        )

    if decision == "approved" and not coa.movements:
        raise HTTPException(status_code=409, detail="Executable COA has no Movement to approve")

    return coa


def coa_decision_time(picture: LogisticsPictureScenario) -> datetime:
    if not picture.event_ledger:
        return datetime(2026, 5, 17, 3, 25, tzinfo=timezone.utc)

    latest_accepted_at = max(event.accepted_at for event in picture.event_ledger)
    return latest_accepted_at.astimezone(timezone.utc) + timedelta(minutes=1)


app = create_app()
