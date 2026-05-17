from collections.abc import Callable
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gallatin_api.event_ledger import (
    AcceptedDomainEvent,
    EventLedgerStore,
    PostgresEventLedgerStore,
)
from gallatin_api.readiness import DependencyStatus, ReadinessResponse, check_postgis
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
        status_code=201,
    )
    def accept_event(event: AcceptedDomainEvent) -> AcceptedDomainEvent:
        return ledger_store.append(event)

    @app.get("/events/accepted", response_model=list[AcceptedDomainEvent])
    def accepted_events() -> list[AcceptedDomainEvent]:
        return ledger_store.list_events()

    return app


app = create_app()
