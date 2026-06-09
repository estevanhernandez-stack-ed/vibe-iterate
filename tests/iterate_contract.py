"""
Reference implementations of the contracts vibe-iterate specifies in prose.

WHY THIS EXISTS
---------------
vibe-iterate ships NO executable code. Its runtime is the LLM following the
SKILL.md procedures. That makes the load-bearing logic — the append/serialize
contract, detect_orphans(), radar staleness, config/cache IO — untestable by
importing a shipped module, because there is none.

These functions are faithful, minimal transcriptions of the documented
contracts so the suite can prove the contracts hold (round-trip correctness,
Windows encoding survival, edge branches) and regression-guard them. The
crown-jewel target is the v1.2.0 fix: "Session + friction log writers — Windows
write-path guidance" (see plugins/vibe-iterate/skills/{friction,session}-logger
/SKILL.md "Append implementation (cross-platform)").

This module is test support. It is NOT shipped with the plugin and is NOT what
the plugin executes at runtime. If the SKILL prose changes, these references
must be updated to match — test_skill_guidance_contract.py guards the prose
side so the two cannot silently diverge.

Stdlib only. No third-party dependencies (the family norm for test code).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# JSONL append / serialize contract
#
# From friction-logger/SKILL.md + session-logger/SKILL.md, "Append
# implementation (cross-platform)":
#   "build the entry as a native object, serialize via the runtime's JSON
#    encoder, write the compact result via the platform's append primitive."
#   Node reference: fs.appendFileSync(file, JSON.stringify(entry) + '\n')
#
# The byte-for-byte intact requirement + the cross-platform note make UTF-8 the
# only safe write/read encoding. On Windows the process default is often cp1252;
# not pinning UTF-8 is the corruption surface this suite guards.
# ---------------------------------------------------------------------------

def serialize_entry(entry: dict) -> str:
    """Serialize one log entry the way the documented contract does: compact,
    one line, no trailing whitespace. ensure_ascii=False keeps real UTF-8 bytes
    (matching JSON.stringify / ConvertTo-Json -Compress, which do not \\uXXXX-
    escape non-ASCII)."""
    return json.dumps(entry, ensure_ascii=False, separators=(",", ":"))


def append_jsonl(path: Path, entry: dict, *, encoding: str = "utf-8") -> None:
    """Append one serialized entry + newline. UTF-8 is the contract; the
    encoding kwarg exists only so tests can demonstrate what breaks when it is
    NOT UTF-8 (the Windows cp1252 regression)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = serialize_entry(entry) + "\n"
    with open(path, "a", encoding=encoding, newline="") as fh:
        fh.write(line)


def read_jsonl(path: Path, *, encoding: str = "utf-8") -> list[dict]:
    """Read a JSONL file, parsing line by line and silently skipping malformed
    lines — exactly the discipline detect_orphans() and :evolve-iterate use
    ("Parse each line; skip malformed lines silently"). Tolerates CRLF: each
    line is stripped of trailing \\r/\\n before parsing."""
    out: list[dict] = []
    text = path.read_text(encoding=encoding)
    for raw in text.split("\n"):
        line = raw.strip("\r").strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return out


def parse_jsonl_strict(text: str) -> list[dict]:
    """Parse every non-empty line, raising on the first malformed one. Used to
    assert that a corrupted line really is unparseable (the silent-drop the
    v1.2.0 fix prevents)."""
    out = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def simulate_double_quote_corruption(json_line: str) -> str:
    """Reproduce the v1.2.0 failure mode the SKILLs warn against:

        "Interior `\"` get escaped to `\\\"`, the leading `{` gets a stray
         space prepended, and the resulting line is unparseable JSON."

    This is what a double-quoted PowerShell `Add-Content -Value "<json>"` does
    to the payload. We model it so a test can assert the result no longer
    parses (and that the recommended single-quoted / ConvertTo-Json path does).
    """
    escaped = json_line.replace('"', '\\"')
    return " " + escaped


# ---------------------------------------------------------------------------
# detect_orphans()  —  friction-logger/SKILL.md "Procedure: detect_orphans()"
# ---------------------------------------------------------------------------

_TERMINAL_OUTCOMES = {"completed", "abandoned", "error", "partial"}


def _parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp with offset or trailing Z."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def detect_orphans(
    session_lines: Iterable[Any],
    existing_friction_lines: Iterable[Any] = (),
    *,
    now: datetime | None = None,
    threshold_hours: int = 24,
) -> list[dict]:
    """Find sentinels (outcome == "in_progress") with no matching terminal
    entry that are older than the threshold, suppressing any already recorded
    as command_abandoned friction.

    session_lines / existing_friction_lines accept already-parsed dicts OR raw
    JSON strings; malformed strings are skipped silently (per the SKILL).
    Returns one orphan dict per orphaned sentinel.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    def _iter_dicts(lines):
        for item in lines:
            if isinstance(item, dict):
                yield item
            elif isinstance(item, str):
                try:
                    yield json.loads(item)
                except (json.JSONDecodeError, ValueError):
                    continue

    sentinels: dict[tuple, datetime] = {}
    terminated: set[tuple] = set()

    for entry in _iter_dicts(session_lines):
        try:
            key = (entry["command"], entry["project_dir"], entry["sessionUUID"])
        except (KeyError, TypeError):
            continue
        outcome = entry.get("outcome")
        if outcome == "in_progress":
            ts_raw = entry.get("timestamp")
            if not ts_raw:
                continue
            try:
                sentinels[key] = _parse_ts(ts_raw)
            except (ValueError, TypeError):
                continue
        elif outcome in _TERMINAL_OUTCOMES:
            terminated.add(key)

    # Already-recorded command_abandoned triples — suppress duplicates.
    already: set[tuple] = set()
    for entry in _iter_dicts(existing_friction_lines):
        if entry.get("friction_type") == "command_abandoned":
            try:
                already.add(
                    (entry["command"], entry["project_dir"], entry["sessionUUID"])
                )
            except (KeyError, TypeError):
                continue

    orphans: list[dict] = []
    cutoff = timedelta(hours=threshold_hours)
    for key, ts in sentinels.items():
        if key in terminated or key in already:
            continue
        age = now - ts
        if age >= cutoff:
            command, project_dir, session_uuid = key
            orphans.append(
                {
                    "command": command,
                    "project_dir": project_dir,
                    "sessionUUID": session_uuid,
                    "sentinel_ts": ts.isoformat(),
                    "age_hours": age.total_seconds() / 3600.0,
                }
            )
    return orphans


# ---------------------------------------------------------------------------
# Radar staleness  —  radar/SKILL.md Step 1
#   "refreshed_at <= 14 days ago -> current"; "> 14 days ago -> stale"
# ---------------------------------------------------------------------------

def is_radar_stale(
    refreshed_at: str | None,
    *,
    now: datetime | None = None,
    max_age_days: int = 14,
) -> bool:
    """True when the radar cache is stale. A missing or unparseable
    refreshed_at is treated as stale (defensive: surface staleness rather than
    trust a bad cache). Exactly max_age_days old counts as current."""
    if now is None:
        now = datetime.now(timezone.utc)
    if not refreshed_at:
        return True
    try:
        ts = _parse_ts(refreshed_at)
    except (ValueError, TypeError):
        return True
    return (now - ts) > timedelta(days=max_age_days)


# ---------------------------------------------------------------------------
# Config / cache IO  (full-file atomic write; UTF-8)
# ---------------------------------------------------------------------------

def dump_json(path: Path, obj: Any, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2), encoding=encoding
    )


def load_json(path: Path, *, encoding: str = "utf-8") -> Any:
    return json.loads(path.read_text(encoding=encoding))


# ---------------------------------------------------------------------------
# Minimal JSON-Schema (draft-2019 subset) validator
#
# Stdlib only — the family rule forbids new test dependencies, and there is no
# stdlib JSON-Schema validator. This covers exactly the keywords the three
# vibe-iterate schemas use: type (incl. unions + null), required,
# additionalProperties(false), properties, enum, items, minLength, minimum,
# format(date-time, uri). The fixtures are the oracle: 5 valid lines must pass,
# 5 invalid lines must each fail — a wrong validator breaks those, so the
# validator is mutually checked against the shipped fixtures.
# ---------------------------------------------------------------------------

_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)
_URI_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://[^\s]+$")

_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def _check_type(value: Any, type_spec: Any) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    return any(_TYPE_CHECKS[t](value) for t in types)


def schema_errors(instance: Any, schema: dict, path: str = "$") -> list[str]:
    """Return a list of human-readable validation errors. Empty list == valid."""
    errors: list[str] = []

    if "type" in schema and not _check_type(instance, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(instance).__name__}")
        # If the type is wrong, deeper checks are noise.
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: {instance!r} != const {schema['const']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        fmt = schema.get("format")
        if fmt == "date-time" and not _DATETIME_RE.match(instance):
            errors.append(f"{path}: {instance!r} is not a valid date-time")
        if fmt == "uri" and not _URI_RE.match(instance):
            errors.append(f"{path}: {instance!r} is not a valid uri")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property {req!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: additional property {key!r} not allowed")
        for key, subschema in props.items():
            if key in instance:
                errors.extend(schema_errors(instance[key], subschema, f"{path}.{key}"))

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(schema_errors(item, schema["items"], f"{path}[{i}]"))

    return errors


def is_valid(instance: Any, schema: dict) -> bool:
    return not schema_errors(instance, schema)
