"""
detect_orphans() — sentinel/terminal pairing, 24h threshold, dedup, edge branches.

From friction-logger/SKILL.md "Procedure: detect_orphans()": index sentinels
(outcome=="in_progress") by (command, project_dir, sessionUUID), mark terminals
(completed/abandoned/error/partial), emit one command_abandoned orphan per
sentinel with no terminal aged >= 24h, and suppress triples already recorded as
command_abandoned. Malformed lines are skipped silently.

This logic is downstream of the serializer: the v1.2.0 corruption made
detect_orphans() false-positive, so its silent-skip-on-malformed branch is part
of the same regression surface.
"""
from datetime import datetime, timedelta, timezone

from iterate_contract import detect_orphans

NOW = datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sentinel(command="feature-add", project="vibe-cartographer",
              uuid="u-1", hours_ago=48):
    ts = NOW - timedelta(hours=hours_ago)
    return {
        "command": command,
        "project_dir": project,
        "sessionUUID": uuid,
        "outcome": "in_progress",
        "timestamp": ts.isoformat(),
    }


def _terminal(command="feature-add", project="vibe-cartographer",
              uuid="u-1", outcome="completed", hours_ago=47):
    ts = NOW - timedelta(hours=hours_ago)
    return {
        "command": command,
        "project_dir": project,
        "sessionUUID": uuid,
        "outcome": outcome,
        "timestamp": ts.isoformat(),
    }


# ---------------------------------------------------------------------------
# Pairing
# ---------------------------------------------------------------------------

def test_paired_sentinel_and_terminal_is_not_orphan():
    lines = [_sentinel(), _terminal(outcome="completed")]
    assert detect_orphans(lines, now=NOW) == []


def test_lone_old_sentinel_is_orphan():
    orphans = detect_orphans([_sentinel(hours_ago=48)], now=NOW)
    assert len(orphans) == 1
    assert orphans[0]["command"] == "feature-add"
    assert orphans[0]["sessionUUID"] == "u-1"
    assert orphans[0]["age_hours"] == 48.0


def test_lone_recent_sentinel_is_not_orphan():
    """Stale-window edge: a sentinel younger than 24h is still in-flight, not
    abandoned."""
    assert detect_orphans([_sentinel(hours_ago=23)], now=NOW) == []


def test_threshold_boundary_is_inclusive_at_24h():
    """Exactly 24h old counts as orphaned (age >= threshold)."""
    assert len(detect_orphans([_sentinel(hours_ago=24)], now=NOW)) == 1
    # One second under 24h is not.
    almost = _sentinel(hours_ago=24)
    almost["timestamp"] = (NOW - timedelta(hours=24) + timedelta(seconds=1)).isoformat()
    assert detect_orphans([almost], now=NOW) == []


def test_all_terminal_outcomes_suppress_orphan():
    for outcome in ("completed", "abandoned", "error", "partial"):
        lines = [_sentinel(), _terminal(outcome=outcome)]
        assert detect_orphans(lines, now=NOW) == [], f"{outcome} should pair"


def test_distinct_uuids_do_not_cross_pair():
    """A terminal for a DIFFERENT session must not satisfy an orphaned sentinel."""
    lines = [_sentinel(uuid="u-1"), _terminal(uuid="u-2", outcome="completed")]
    orphans = detect_orphans(lines, now=NOW)
    assert len(orphans) == 1
    assert orphans[0]["sessionUUID"] == "u-1"


def test_same_command_different_project_are_distinct():
    lines = [
        _sentinel(project="app-a", uuid="u-1"),
        _terminal(project="app-b", uuid="u-1", outcome="completed"),
    ]
    orphans = detect_orphans(lines, now=NOW)
    assert len(orphans) == 1
    assert orphans[0]["project_dir"] == "app-a"


# ---------------------------------------------------------------------------
# Dedup against existing friction
# ---------------------------------------------------------------------------

def test_existing_command_abandoned_suppresses_duplicate():
    sentinel = _sentinel(uuid="u-9")
    existing = [{
        "friction_type": "command_abandoned",
        "command": "feature-add",
        "project_dir": "vibe-cartographer",
        "sessionUUID": "u-9",
    }]
    assert detect_orphans([sentinel], existing, now=NOW) == []


def test_non_abandoned_friction_does_not_suppress():
    sentinel = _sentinel(uuid="u-9")
    existing = [{
        "friction_type": "complement_rejected",
        "command": "feature-add",
        "project_dir": "vibe-cartographer",
        "sessionUUID": "u-9",
    }]
    assert len(detect_orphans([sentinel], existing, now=NOW)) == 1


# ---------------------------------------------------------------------------
# Edge branches — malformed / empty / mixed input
# ---------------------------------------------------------------------------

def test_malformed_json_line_is_skipped_not_fatal():
    """A corrupted line (the v1.2.0 silent-drop case) must be skipped without
    crashing, and must not block detection of a real orphan on a later line."""
    lines = [
        '{ this is not valid json',
        '  {\\"command\\":\\"feature-add\\"}',  # double-quote corruption artifact
        _sentinel(uuid="u-real", hours_ago=30),
    ]
    orphans = detect_orphans(lines, now=NOW)
    assert len(orphans) == 1
    assert orphans[0]["sessionUUID"] == "u-real"


def test_empty_input_yields_no_orphans():
    assert detect_orphans([], now=NOW) == []


def test_sentinel_missing_required_key_is_skipped():
    broken = {"outcome": "in_progress", "timestamp": NOW.isoformat()}  # no triple
    assert detect_orphans([broken], now=NOW) == []


def test_sentinel_with_bad_timestamp_is_skipped():
    bad = _sentinel()
    bad["timestamp"] = "not-a-timestamp"
    assert detect_orphans([bad], now=NOW) == []


def test_accepts_raw_json_strings_and_dicts_interchangeably():
    import json
    lines = [json.dumps(_sentinel(uuid="u-str")), _sentinel(uuid="u-dict")]
    orphans = detect_orphans(lines, now=NOW)
    uuids = sorted(o["sessionUUID"] for o in orphans)
    assert uuids == ["u-dict", "u-str"]


def test_mixed_batch_returns_only_true_orphans():
    lines = [
        _sentinel(uuid="paired"), _terminal(uuid="paired", outcome="completed"),
        _sentinel(uuid="old-orphan", hours_ago=72),
        _sentinel(uuid="fresh", hours_ago=2),
    ]
    orphans = detect_orphans(lines, now=NOW)
    assert [o["sessionUUID"] for o in orphans] == ["old-orphan"]
