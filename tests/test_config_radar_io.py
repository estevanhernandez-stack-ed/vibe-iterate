"""
Config + radar-cache IO round-trip.

bootstrap writes .vibe-iterate/config.json; radar writes
.vibe-iterate/radar.cache.json (full-file atomic write, per radar/SKILL.md
Step 3). Both are read back by later runs. These tests prove the read/write
round-trip is lossless under UTF-8 (including unicode category names and
competitor URLs) and that the documented "config absent / malformed" branches
surface as catchable errors rather than silent bad state.
"""
import json

import pytest

from conftest import FIXTURES_DIR
from iterate_contract import dump_json, load_json


def _config_fixture() -> dict:
    return json.loads((FIXTURES_DIR / "config.valid.json").read_text(encoding="utf-8"))


def _radar_fixture() -> dict:
    return json.loads((FIXTURES_DIR / "radar-cache.valid.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

def test_config_round_trip_is_lossless(tmp_path):
    cfg = _config_fixture()
    path = tmp_path / ".vibe-iterate" / "config.json"
    dump_json(path, cfg)
    assert load_json(path) == cfg


def test_radar_cache_round_trip_is_lossless(tmp_path):
    cache = _radar_fixture()
    path = tmp_path / ".vibe-iterate" / "radar.cache.json"
    dump_json(path, cache)
    assert load_json(path) == cache


def test_config_unicode_category_round_trips(tmp_path):
    """A category or competitor list with non-ASCII must survive write+read on
    Windows — the same UTF-8 pin the loggers require applies to full-file IO."""
    cfg = _config_fixture()
    cfg["category"] = "AI 笔记 app — café edition"
    path = tmp_path / "config.json"
    dump_json(path, cfg)
    assert load_json(path)["category"] == "AI 笔记 app — café edition"
    # And the on-disk bytes are real UTF-8.
    assert "café".encode("utf-8") in path.read_bytes()


def test_dump_creates_missing_parent_dir(tmp_path):
    """Mirrors 'create the directory if missing' — the first write into a fresh
    .vibe-iterate/ must not fail on the absent folder."""
    path = tmp_path / "deeply" / "nested" / ".vibe-iterate" / "config.json"
    dump_json(path, {"category": "x", "competitors": [], "framework_pins": [],
                     "last_inferred_at": "2026-05-04T15:30:00Z"})
    assert path.exists()


# ---------------------------------------------------------------------------
# Edge branches — absent / empty / malformed
# ---------------------------------------------------------------------------

def test_missing_config_raises_file_not_found(tmp_path):
    """The radar/SKILL.md 'config absent' branch hinges on a detectable miss."""
    with pytest.raises(FileNotFoundError):
        load_json(tmp_path / "nope.json")


def test_empty_config_file_raises_json_error(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_json(path)


def test_truncated_config_raises_json_error(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"category": "x", "competitors": [', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_json(path)


def test_full_file_write_replaces_not_appends(tmp_path):
    """Radar cache write is atomic full-file, never append — a second write must
    not leave stale trailing content from a larger first write."""
    path = tmp_path / "radar.cache.json"
    big = _radar_fixture()
    dump_json(path, big)
    small = {"refreshed_at": "2026-06-01T00:00:00Z", "framework_releases": [],
             "competitor_changes": [], "product_hunt_buzz": []}
    dump_json(path, small)
    assert load_json(path) == small
