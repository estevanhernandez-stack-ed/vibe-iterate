"""
Schema <-> fixture contract for the three shipped JSON Schemas.

The plugin's only declarative artifacts are
plugins/vibe-iterate/skills/guide/schemas/{atlas-entry,config,radar-cache}
.schema.json and their fixtures. The agent validates Atlas lines / config /
radar cache against these before writing. This suite proves:
  - every line of *.valid.jsonl / *.valid.json conforms,
  - every line of *.invalid.jsonl is rejected (and names which constraint),
  - constructed negatives exercise constraints the fixtures don't cover.

Validation uses the stdlib subset validator in iterate_contract (no third-party
jsonschema dep, per the family stdlib-only rule). The shipped fixtures are the
oracle: if the validator were wrong, the 5 valid / 5 invalid lines would break.
"""
import json

import pytest

from conftest import SCHEMAS_DIR, FIXTURES_DIR
from iterate_contract import schema_errors, is_valid


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _read_jsonl_lines(name: str) -> list[dict]:
    text = (FIXTURES_DIR / name).read_text(encoding="utf-8")
    return [json.loads(ln) for ln in text.splitlines() if ln.strip()]


ATLAS_SCHEMA = _load_schema("atlas-entry.schema.json")
CONFIG_SCHEMA = _load_schema("config.schema.json")
RADAR_SCHEMA = _load_schema("radar-cache.schema.json")

VALID_ATLAS = _read_jsonl_lines("atlas-entry.valid.jsonl")
INVALID_ATLAS = _read_jsonl_lines("atlas-entry.invalid.jsonl")


# ---------------------------------------------------------------------------
# Shipped fixtures conform (or are correctly rejected)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("entry", VALID_ATLAS, ids=lambda e: e.get("title", "?")[:30])
def test_valid_atlas_fixtures_pass(entry):
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert errors == [], f"valid fixture rejected: {errors}"


@pytest.mark.parametrize("entry", INVALID_ATLAS, ids=lambda e: e.get("title", "?")[:30])
def test_invalid_atlas_fixtures_fail(entry):
    assert not is_valid(entry, ATLAS_SCHEMA), f"invalid fixture wrongly accepted: {entry}"


def test_we_actually_loaded_the_fixtures():
    """Guard against an empty-glob false-green: the fixture counts are known."""
    assert len(VALID_ATLAS) == 4
    assert len(INVALID_ATLAS) == 5


def test_config_fixture_passes():
    cfg = json.loads((FIXTURES_DIR / "config.valid.json").read_text(encoding="utf-8"))
    assert schema_errors(cfg, CONFIG_SCHEMA) == []


def test_radar_cache_fixture_passes():
    cache = json.loads((FIXTURES_DIR / "radar-cache.valid.json").read_text(encoding="utf-8"))
    assert schema_errors(cache, RADAR_SCHEMA) == []


# ---------------------------------------------------------------------------
# The invalid fixtures fail for the RIGHT reason (named constraint)
# ---------------------------------------------------------------------------

def test_invalid_line_missing_required_ts():
    entry = {"mode": "feature-add", "outcome": "shipped", "title": "missing ts field"}
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("required" in e and "ts" in e for e in errors)


def test_invalid_line_bad_ts_format():
    entry = {"ts": "not-a-valid-timestamp", "mode": "feature-add", "outcome": "shipped",
             "title": "x", "rationale": "x", "rejected_runners_up": [], "pr": None}
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("date-time" in e for e in errors)


def test_invalid_line_bad_mode_enum():
    entry = {"ts": "2026-05-04T15:30:00Z", "mode": "unknown-mode", "outcome": "shipped",
             "title": "x", "rationale": "x", "rejected_runners_up": [], "pr": None}
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("enum" in e and "mode" in e for e in errors)


def test_invalid_line_bad_outcome_enum():
    entry = {"ts": "2026-05-04T15:30:00Z", "mode": "feature-add", "outcome": "maybe",
             "title": "x", "rationale": "x", "rejected_runners_up": [], "pr": None}
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("enum" in e and "outcome" in e for e in errors)


def test_invalid_line_bad_source_enum():
    entry = {"ts": "2026-05-25T18:01:00Z", "mode": "horizon", "outcome": "queued",
             "title": "x", "rationale": "x", "rejected_runners_up": [], "pr": None,
             "source": "not-a-known-source"}
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("source" in e and "enum" in e for e in errors)


# ---------------------------------------------------------------------------
# Constructed negatives — constraints the fixtures don't exercise
# ---------------------------------------------------------------------------

def _valid_atlas() -> dict:
    return {
        "ts": "2026-05-04T15:30:00Z", "mode": "feature-add", "outcome": "shipped",
        "title": "ok", "rationale": "because", "rejected_runners_up": ["a"],
        "pr": "https://github.com/x/y/pull/1",
    }


def test_additional_property_rejected():
    entry = _valid_atlas()
    entry["surprise"] = "extra"
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("additional property" in e for e in errors)


def test_wrong_type_for_title_rejected():
    entry = _valid_atlas()
    entry["title"] = 123
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any(e.startswith("$.title") for e in errors)


def test_empty_title_violates_min_length():
    entry = _valid_atlas()
    entry["title"] = ""
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("minLength" in e for e in errors)


def test_pr_accepts_string_or_null_union():
    null_pr = _valid_atlas(); null_pr["pr"] = None; null_pr["outcome"] = "rejected"
    str_pr = _valid_atlas()
    assert is_valid(null_pr, ATLAS_SCHEMA)
    assert is_valid(str_pr, ATLAS_SCHEMA)


def test_rejected_runners_up_must_be_array_of_strings():
    entry = _valid_atlas()
    entry["rejected_runners_up"] = [1, 2, 3]
    errors = schema_errors(entry, ATLAS_SCHEMA)
    assert any("rejected_runners_up" in e for e in errors)


def test_config_framework_pin_missing_version_rejected():
    cfg = {
        "category": "x", "competitors": ["https://a.com"],
        "framework_pins": [{"name": "next"}],  # missing version
        "last_inferred_at": "2026-05-04T15:30:00Z",
    }
    errors = schema_errors(cfg, CONFIG_SCHEMA)
    assert any("version" in e and "required" in e for e in errors)


def test_config_competitor_must_be_uri():
    cfg = {
        "category": "x", "competitors": ["not a url"],
        "framework_pins": [], "last_inferred_at": "2026-05-04T15:30:00Z",
    }
    errors = schema_errors(cfg, CONFIG_SCHEMA)
    assert any("uri" in e for e in errors)


def test_radar_votes_minimum_zero_enforced():
    cache = {
        "refreshed_at": "2026-05-04T14:00:00Z",
        "framework_releases": [], "competitor_changes": [],
        "product_hunt_buzz": [{
            "name": "x", "tagline": "y", "url": "https://ph.com/x", "votes": -5,
        }],
    }
    errors = schema_errors(cache, RADAR_SCHEMA)
    assert any("minimum" in e for e in errors)


def test_radar_boolean_field_rejects_non_boolean():
    cache = {
        "refreshed_at": "2026-05-04T14:00:00Z",
        "framework_releases": [{
            "package": "next", "current_pin": "1", "latest": "2",
            "highlights": [], "codemod_available": "yes", "breaking": False,
        }],
        "competitor_changes": [], "product_hunt_buzz": [],
    }
    errors = schema_errors(cache, RADAR_SCHEMA)
    assert any("codemod_available" in e for e in errors)
