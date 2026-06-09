"""
Guard the shipped SKILL prose that the executable contracts transcribe.

vibe-iterate's runtime is the LLM following SKILL.md. The reference functions in
iterate_contract.py are only faithful if the prose still says what they assume.
These tests assert the load-bearing guidance lines are still present, so a future
edit that re-introduces the v1.2.0 failure mode (or drops the UTF-8 pin) trips a
test instead of silently regressing the real "implementation."
"""
import re

from conftest import SKILLS_DIR

LOGGERS = ["friction-logger", "session-logger"]


def _skill_text(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The v1.2.0 append-implementation guidance must persist in BOTH loggers
# ---------------------------------------------------------------------------

def test_loggers_have_cross_platform_append_section():
    for name in LOGGERS:
        text = _skill_text(name)
        assert "Append implementation (cross-platform)" in text, name


def test_loggers_recommend_compact_json_serialize():
    """The serialize-then-append path (ConvertTo-Json -Compress / JSON.stringify)
    is the fix. It must remain the recommended path in both loggers."""
    for name in LOGGERS:
        text = _skill_text(name)
        assert "ConvertTo-Json -Compress" in text, name
        assert "JSON.stringify(entry)" in text, name


def test_loggers_pin_utf8_on_powershell_write():
    """The Windows write path must keep the explicit UTF-8 encoding pin —
    dropping it is the cp1252 corruption surface this suite guards."""
    for name in LOGGERS:
        text = _skill_text(name)
        assert "-Encoding utf8" in text, name


def test_loggers_warn_against_double_quoted_append():
    """The exact anti-pattern that caused v1.2.0 must stay flagged as 'avoid'."""
    for name in LOGGERS:
        text = _skill_text(name).lower()
        assert "avoid" in text
        assert "double-quote" in text or "double quoted" in text or "double-quoted" in text
        assert "v1.2.0" in _skill_text(name)


# ---------------------------------------------------------------------------
# detect_orphans contract anchors
# ---------------------------------------------------------------------------

def test_friction_logger_documents_24h_orphan_threshold():
    text = _skill_text("friction-logger")
    assert "detect_orphans" in text
    assert re.search(r"24\s*hours?", text), "24h orphan threshold must be documented"


def test_friction_logger_lists_terminal_outcomes():
    """The terminal-outcome set the reference uses must match the prose."""
    text = _skill_text("friction-logger")
    for outcome in ("completed", "abandoned", "error", "partial"):
        assert outcome in text, outcome


def test_command_abandoned_only_emitted_by_detect_orphans():
    text = _skill_text("friction-logger")
    assert "command_abandoned" in text
    assert "detect_orphans()" in text
