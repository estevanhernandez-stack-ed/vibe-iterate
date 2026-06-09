"""
JSONL append/serialize contract — round-trip + Windows encoding regressions.

This is the crown-jewel module. The v1.2.0 release fixed "Session + friction log
writers — Windows write-path guidance": entries written via double-quoted
PowerShell append got their interior `"` escaped to `\\"` and a stray leading
space prepended, producing JSON that :evolve-iterate silently dropped on parse
and detect_orphans() then false-positived against (~18% corruption rate on
2026-05-28). The serializer contract lives in prose
(friction-logger / session-logger SKILL.md "Append implementation"); these tests
make it executable and regression-guard it.

Windows encoding round-trips (UTF-8 / CRLF / cp1252) are first-class here:
on Windows the process default encoding is often cp1252, so the only safe
write/read path is an explicit UTF-8 pin — exactly what the SKILLs prescribe
(`Add-Content -Encoding utf8`).
"""
import json
from datetime import datetime, timezone

import pytest

from iterate_contract import (
    append_jsonl,
    read_jsonl,
    serialize_entry,
    simulate_double_quote_corruption,
    parse_jsonl_strict,
)


# ---------------------------------------------------------------------------
# Sample entries — realistic friction + session shapes, including the exact
# fields most likely to carry hostile characters (symptom, friction_notes).
# ---------------------------------------------------------------------------

def _friction_entry(**overrides) -> dict:
    base = {
        "schema_version": 1,
        "timestamp": "2026-05-06T14:42:00-05:00",
        "plugin": "vibe-iterate",
        "plugin_version": "1.2.0",
        "command": "feature-add",
        "project_dir": "vibe-cartographer",
        "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
        "friction_type": "complement_rejected",
        "confidence": "high",
        "complement_involved": "vibe-cartographer",
        "symptom": 'User declined Cart-delegation upsell at "heavy-iteration" check.',
    }
    base.update(overrides)
    return base


def _session_entry(**overrides) -> dict:
    base = {
        "schema_version": 1,
        "timestamp": "2026-05-06T14:25:00-05:00",
        "plugin": "vibe-iterate",
        "plugin_version": "1.2.0",
        "command": "feature-add",
        "project_dir": "vibe-cartographer",
        "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
        "outcome": "in_progress",
    }
    base.update(overrides)
    return base


# Characters that are NOT representable in cp1252 — the mojibake surface.
NON_CP1252 = "emoji=🚀 cjk=日本語 zwj=👩‍💻"
# Characters that ARE in cp1252 but differ from latin-1/ascii — smart quotes,
# em-dash, accents. These are the everyday strings that still corrupt under a
# wrong encoding pairing.
CP1252_SPECIALS = "smart=“quotes” dash=— accent=café — résumé"


# ---------------------------------------------------------------------------
# Round-trip correctness — the core serializer contract
# ---------------------------------------------------------------------------

def test_ascii_round_trip(tmp_path):
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry()
    append_jsonl(path, entry)
    assert read_jsonl(path) == [entry]


def test_interior_double_quotes_survive(tmp_path):
    """The exact v1.2.0 trigger: a value containing literal `"` must round-trip
    intact, not arrive escaped/mangled."""
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry(symptom='said "ship it" then "wait, no"')
    append_jsonl(path, entry)
    [got] = read_jsonl(path)
    assert got["symptom"] == 'said "ship it" then "wait, no"'


def test_unicode_round_trip_utf8(tmp_path):
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry(symptom=f"{CP1252_SPECIALS} {NON_CP1252}")
    append_jsonl(path, entry)
    [got] = read_jsonl(path)
    assert got["symptom"] == entry["symptom"]


def test_multiple_appends_are_line_separated(tmp_path):
    path = tmp_path / "sessions.jsonl"
    e1 = _session_entry(outcome="in_progress")
    e2 = _session_entry(outcome="completed", atlas_outcome="shipped")
    append_jsonl(path, e1)
    append_jsonl(path, e2)
    got = read_jsonl(path)
    assert got == [e1, e2]
    # Exactly one entry per physical line, newline-terminated.
    raw = path.read_text(encoding="utf-8")
    assert raw.endswith("\n")
    assert len([ln for ln in raw.split("\n") if ln]) == 2


def test_serialized_line_has_no_embedded_newline(tmp_path):
    """A newline inside a string value must be JSON-escaped, never emitted raw —
    otherwise it splits one logical entry across two JSONL lines."""
    entry = _friction_entry(symptom="line one\nline two")
    line = serialize_entry(entry)
    assert "\n" not in line
    assert "\\n" in line


# ---------------------------------------------------------------------------
# Windows encoding regressions — FIRST-CLASS
# ---------------------------------------------------------------------------

def test_written_bytes_are_utf8(tmp_path):
    """The contract serializes real UTF-8 bytes (ensure_ascii=False), and the
    file must decode cleanly as UTF-8."""
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry(symptom=NON_CP1252)
    append_jsonl(path, entry)
    raw = path.read_bytes()
    # Decodes as UTF-8 without error...
    decoded = raw.decode("utf-8")
    assert NON_CP1252 in decoded
    # ...and the emoji is present as multi-byte UTF-8, not an escape artifact.
    assert "🚀".encode("utf-8") in raw


def test_cp1252_read_of_utf8_file_corrupts_non_cp1252(tmp_path):
    """Regression witness: reading a UTF-8 file as cp1252 (the Windows process
    default) mojibakes non-cp1252 characters. This is why the read path MUST
    pin UTF-8. The correct UTF-8 read round-trips; the cp1252 read does not."""
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry(symptom=NON_CP1252)
    append_jsonl(path, entry)

    # Correct: UTF-8 read is lossless.
    [utf8_got] = read_jsonl(path, encoding="utf-8")
    assert utf8_got["symptom"] == NON_CP1252

    # Wrong: cp1252 read either raises or yields mojibake — never the original.
    try:
        cp = read_jsonl(path, encoding="cp1252")
    except (UnicodeDecodeError, ValueError):
        cp = None
    if cp:
        # If it decoded at all, the symptom must be corrupted (mojibake), proving
        # the wrong-encoding hazard.
        assert cp[0].get("symptom") != NON_CP1252


def test_cp1252_write_is_lossy_for_non_cp1252(tmp_path):
    """Witness the WRITE half of the bug: serializing real UTF-8 bytes through a
    cp1252 writer (errors='replace', the only way it doesn't crash) drops the
    emoji to '?'. UTF-8 write preserves it. Encoding must be pinned on write."""
    path_bad = tmp_path / "bad.jsonl"
    entry = _friction_entry(symptom=NON_CP1252)
    line = serialize_entry(entry) + "\n"

    # cp1252 cannot represent the emoji/CJK — replacement is lossy.
    bad_bytes = line.encode("cp1252", errors="replace")
    path_bad.write_bytes(bad_bytes)
    reloaded = json.loads(path_bad.read_text(encoding="cp1252").strip())
    assert reloaded["symptom"] != NON_CP1252
    assert "?" in reloaded["symptom"]

    # UTF-8 write is lossless.
    path_good = tmp_path / "good.jsonl"
    append_jsonl(path_good, entry)
    assert read_jsonl(path_good)[0]["symptom"] == NON_CP1252


def test_cp1252_specials_round_trip_under_utf8(tmp_path):
    """Smart quotes / em-dash / accents are the everyday (non-emoji) strings
    that still corrupt under a wrong encoding. UTF-8 round-trips them."""
    path = tmp_path / "friction.jsonl"
    entry = _friction_entry(symptom=CP1252_SPECIALS)
    append_jsonl(path, entry)
    assert read_jsonl(path)[0]["symptom"] == CP1252_SPECIALS


def test_crlf_terminated_lines_still_parse(tmp_path):
    """A file written with CRLF line endings (Windows text mode, or git
    autocrlf) must still parse line-by-line. The reader strips trailing \\r."""
    path = tmp_path / "friction.jsonl"
    e1 = _friction_entry(symptom="first")
    e2 = _friction_entry(symptom="second")
    crlf_blob = serialize_entry(e1) + "\r\n" + serialize_entry(e2) + "\r\n"
    path.write_text(crlf_blob, encoding="utf-8", newline="")
    got = read_jsonl(path)
    assert [g["symptom"] for g in got] == ["first", "second"]


def test_json_loads_tolerates_trailing_cr():
    """Lower-level guarantee behind the CRLF test: a lone trailing \\r is
    insignificant whitespace to json.loads."""
    assert json.loads('{"a":1}\r') == {"a": 1}


def test_utf8_bom_breaks_strict_parse():
    """Finding: PowerShell 5.1 `Add-Content -Encoding utf8` writes a UTF-8 BOM.
    A BOM on the first line breaks a strict json.loads (it becomes \\ufeff{...}).
    pwsh 7+ `-Encoding utf8` is BOM-less, so the env this was built on is safe —
    but the SKILL guidance does not call out the PS 5.1 hazard. Captured here as
    a regression witness: if guidance ever moves to a BOM-emitting writer, the
    first line will silent-drop exactly like the v1.2.0 bug."""
    line = serialize_entry(_friction_entry())
    bom_line = "﻿" + line
    with pytest.raises(json.JSONDecodeError):
        json.loads(bom_line)
    # The defensive read (utf-8-sig) would recover it; the strict path does not.
    assert json.loads(bom_line.encode("utf-8").decode("utf-8-sig")) is not None


# ---------------------------------------------------------------------------
# v1.2.0 double-quote corruption — regression guard
# ---------------------------------------------------------------------------

def test_double_quote_corruption_is_unparseable():
    """The documented failure mode: double-quoted PowerShell append escapes
    interior `"` to `\\"` and prepends a stray space. Assert the result is the
    silent-drop case (unparseable), while the clean serialized line parses."""
    clean = serialize_entry(_friction_entry())
    # Sanity: the recommended path produces parseable JSON.
    assert json.loads(clean)["plugin"] == "vibe-iterate"

    corrupted = simulate_double_quote_corruption(clean)
    with pytest.raises(json.JSONDecodeError):
        json.loads(corrupted)


def test_corrupted_line_silent_drops_in_lenient_reader(tmp_path):
    """End-to-end: a file with one clean line and one corrupted line yields only
    the clean entry from the lenient reader (silent-drop), reproducing why
    detect_orphans() under-counted before v1.2.0 rather than crashing."""
    path = tmp_path / "friction.jsonl"
    clean_entry = _friction_entry(symptom="clean")
    clean = serialize_entry(clean_entry)
    corrupted = simulate_double_quote_corruption(
        serialize_entry(_friction_entry(symptom="corrupted"))
    )
    path.write_text(clean + "\n" + corrupted + "\n", encoding="utf-8", newline="")

    got = read_jsonl(path)
    assert len(got) == 1
    assert got[0]["symptom"] == "clean"

    # The strict parser proves the second line really was malformed.
    with pytest.raises(json.JSONDecodeError):
        parse_jsonl_strict(path.read_text(encoding="utf-8"))


def test_recommended_path_survives_what_corruption_destroys(tmp_path):
    """The positive twin: the same entry that the double-quote path destroys
    round-trips perfectly through the recommended serialize-then-append path,
    interior quotes and all."""
    entry = _friction_entry(symptom='nested "quote" payload')
    path = tmp_path / "friction.jsonl"
    append_jsonl(path, entry)
    assert read_jsonl(path)[0]["symptom"] == 'nested "quote" payload'
