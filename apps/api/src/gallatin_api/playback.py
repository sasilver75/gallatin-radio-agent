import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class ScenarioPlaybackStep(BaseModel):
    step_id: str
    sequence: int
    narrative_time: str
    title: str
    summary: str
    action: Literal[
        "transmit_prerecorded_clip",
        "accept_proposed_interpretation",
        "approve_executable_coa",
    ]
    clip_id: str | None = None
    interpretation_id: str | None = None
    coa_id: str | None = None


class ScenarioPlayback(BaseModel):
    scenario_id: str
    title: str
    description: str
    steps: list[ScenarioPlaybackStep]


DEFAULT_PLAYBACK_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "scenarios"
    / "kaohsiung_tainan_playback.json"
)


@lru_cache(maxsize=1)
def load_kaohsiung_tainan_playback(
    path: Path = DEFAULT_PLAYBACK_PATH,
) -> ScenarioPlayback:
    return ScenarioPlayback.model_validate(json.loads(path.read_text(encoding="utf-8")))
