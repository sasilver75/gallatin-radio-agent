from collections.abc import Callable
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gallatin_api.event_ledger import (
    AcceptedDomainEvent,
    EventLedgerStore,
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
    accepted_denied_area_event_for_interpretation,
    interpret_radio_transmission,
)
from gallatin_api.scenario import (
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

        return transmission.model_copy(update={"interpretations": interpreted.interpretations})

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


app = create_app()
