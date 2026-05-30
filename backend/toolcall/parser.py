from __future__ import annotations

import json
import re

from backend.toolcall.fallback_textkv import parse_textkv_format
from backend.toolcall.formats_json import parse_json_format
from backend.toolcall.formats_xml import parse_xml_format
from backend.toolcall.normalize import normalize_arguments, normalize_tool_name


def _parse_tool_call_marker_format(text: str, allowed_names: set[str]) -> list[dict[str, object]]:
    """Parse ##TOOL_CALL##...##END_CALL## text marker format."""
    tc_m = re.search(r'##TOOL_CALL##\s*(.*?)\s*##END_CALL##', text, re.DOTALL | re.IGNORECASE)
    if not tc_m:
        return []
    try:
        obj = json.loads(tc_m.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        return []

    if not isinstance(obj, dict):
        return []

    name = obj.get("name", "")
    if not isinstance(name, str) or not name:
        return []

    raw_input = obj.get("input", obj.get("args", obj.get("arguments", obj.get("parameters", {}))))
    if isinstance(raw_input, str):
        try:
            raw_input = json.loads(raw_input)
        except (json.JSONDecodeError, TypeError, ValueError):
            raw_input = {"value": raw_input}

    return [{
        "name": normalize_tool_name(name, allowed_names),
        "input": normalize_arguments(raw_input),
    }]


def _has_tool_call_marker_syntax(text: str) -> bool:
    """Check if text contains ##TOOL_CALL##...##END_CALL## marker."""
    lowered = text.lower()
    return "##tool_call##" in lowered and "##end_call##" in lowered


def _has_top_level_json_tool_syntax(text: str) -> bool:
    # Also detect ##TOOL_CALL## marker format
    if _has_tool_call_marker_syntax(text):
        return True
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.removeprefix("```json").removeprefix("```").strip()
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()

    if not stripped.startswith("{"):
        return False

    repaired = stripped.replace('"name="', '"name": "')
    if '"name=' in repaired:
        return True

    try:
        payload = json.loads(repaired)
    except (json.JSONDecodeError, TypeError, ValueError):
        return False

    if not isinstance(payload, dict):
        return False

    if isinstance(payload.get("tool_calls"), list):
        return True

    has_name = isinstance(payload.get("name"), str) and bool(payload.get("name"))
    has_args = any(key in payload for key in ("input", "arguments", "args", "parameters"))
    return has_name and has_args


def _has_xml_like_tool_syntax(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in ("<invoke", "<tool_call", "</tool_call>"))


def parse_tool_calls_detailed(text: str, allowed_names: set[str]) -> dict[str, object]:
    # Try ##TOOL_CALL## marker format first (highest priority for Claude Code profile)
    marker_calls = _parse_tool_call_marker_format(text, allowed_names)
    if marker_calls:
        return {
            "calls": marker_calls,
            "source": "tcmarker",
            "saw_tool_syntax": True,
        }

    candidates = [
        ("json", parse_json_format(text, allowed_names)),
        ("xml", parse_xml_format(text, allowed_names)),
        ("textkv", parse_textkv_format(text, allowed_names)),
    ]

    for source, calls in candidates:
        if calls:
            return {
                "calls": calls,
                "source": source,
                "saw_tool_syntax": True,
            }

    return {
        "calls": [],
        "source": None,
        "saw_tool_syntax": (
            _has_top_level_json_tool_syntax(text)
            or _has_xml_like_tool_syntax(text)
            or any(marker in text for marker in ("function.name:", "function.arguments:", '"name="'))
        ),
    }
