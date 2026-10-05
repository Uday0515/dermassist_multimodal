from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_component = components.declare_component(
    "press_hold_recorder",
    path=str(Path(__file__).parent / "press_hold_recorder"),
)


def press_hold_recorder(*, key: str) -> dict[str, Any] | None:
    return _component(key=key, default=None)
