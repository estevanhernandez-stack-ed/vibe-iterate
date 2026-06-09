"""
Radar cache staleness boundary.

radar/SKILL.md Step 1: refreshed_at <= 14 days ago -> current; > 14 days ago ->
stale (surface staleness, ask before refresh; never auto-refresh). These tests
pin the boundary and the defensive treatment of missing/garbage timestamps.
"""
from datetime import datetime, timedelta, timezone

from iterate_contract import is_radar_stale

NOW = datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc)


def _ago(**kw) -> str:
    return (NOW - timedelta(**kw)).isoformat()


def test_fresh_cache_is_current():
    assert is_radar_stale(_ago(days=1), now=NOW) is False


def test_one_day_under_threshold_is_current():
    assert is_radar_stale(_ago(days=13, hours=23), now=NOW) is False


def test_exactly_fourteen_days_is_current():
    """SKILL: '<= 14 days ago -> current'. The boundary is inclusive."""
    assert is_radar_stale(_ago(days=14), now=NOW) is False


def test_just_over_fourteen_days_is_stale():
    assert is_radar_stale(_ago(days=14, seconds=1), now=NOW) is True


def test_fifteen_days_is_stale():
    assert is_radar_stale(_ago(days=15), now=NOW) is True


def test_missing_refreshed_at_is_stale():
    """Defensive default: no timestamp -> treat as stale rather than trust it."""
    assert is_radar_stale(None, now=NOW) is True
    assert is_radar_stale("", now=NOW) is True


def test_garbage_refreshed_at_is_stale():
    assert is_radar_stale("yesterday-ish", now=NOW) is True


def test_z_suffix_and_offset_timestamps_both_parse():
    z = "2026-05-19T12:00:00Z"        # 1 day before NOW, UTC
    offset = "2026-05-19T07:00:00-05:00"  # same instant, offset form
    assert is_radar_stale(z, now=NOW) is False
    assert is_radar_stale(offset, now=NOW) is False
