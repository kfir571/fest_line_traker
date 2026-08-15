"""
Focused tests for cross-midnight (overnight) time-range support in
backend/api/routes_analytics.py — recommendation() and hourly_graph().

No live Postgres is available in this environment, so `get_db_connection`
is monkeypatched with a fake cursor that records the exact SQL text and
params passed to `execute()` and returns canned rows. This verifies the
actual new logic (validation boundaries, overnight branching, weekday
pairing via (w+1)%7, and SQL ordering) precisely, without needing a
database. Run with: `python3 -m pytest backend/tests -q` from the repo root,
or `python3 -m pytest tests -q` from `backend/`.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from api import create_app
import api.routes_analytics as routes_analytics


class FakeCursor:
    """Records the SQL + params passed to execute(); returns canned rows."""

    def __init__(self, rows):
        self._rows = rows
        self.last_query = None
        self.last_params = None

    def execute(self, query, params):
        self.last_query = query
        self.last_params = params

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeConn:
    def __init__(self, rows):
        self.cursor_obj = FakeCursor(rows)

    def cursor(self):
        return self.cursor_obj

    def close(self):
        pass


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


def install_fake_db(monkeypatch, rows=None):
    """Patches get_db_connection used inside routes_analytics and returns
    the FakeConn so the test can inspect last_query/last_params afterward."""
    conn = FakeConn(rows or [])
    monkeypatch.setattr(routes_analytics, "get_db_connection", lambda: conn)
    return conn


# ---------------------------------------------------------------------------
# hourly_graph()
# ---------------------------------------------------------------------------

def test_hourly_graph_same_day_unchanged(client, monkeypatch):
    """10 -> 13 must keep using the original single-condition query (no OR,
    no CASE), proving same-day behavior is untouched."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/hourly-graph?weekday=2&from_hour=10&to_hour=13")
    assert resp.status_code == 200
    q = conn.cursor_obj.last_query
    assert q.count("weekday = %s") == 1
    assert "CASE" not in q
    assert conn.cursor_obj.last_params == (2, 10, 13)


def test_hourly_graph_overnight_22_to_1(client, monkeypatch):
    """22 -> 1: must query weekday's late segment OR (weekday+1)%7's early
    segment, and order with a CASE so the day boundary stays chronological."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/hourly-graph?weekday=1&from_hour=22&to_hour=1")
    assert resp.status_code == 200
    q = conn.cursor_obj.last_query
    assert q.count("weekday = %s") == 3  # 2 WHERE conditions + 1 CASE
    assert "CASE WHEN weekday = %s THEN 0 ELSE 1 END" in q
    # weekday=1 (Tue), from=22, next_weekday=2 (Wed), to=1, case-weekday=1
    assert conn.cursor_obj.last_params == (1, 22, 2, 1, 1)


def test_hourly_graph_week_boundary_sunday_to_monday(client, monkeypatch):
    """Sunday (6) -> Monday (0): (6+1)%7 must wrap to 0, not 7."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/hourly-graph?weekday=6&from_hour=22&to_hour=1")
    assert resp.status_code == 200
    assert conn.cursor_obj.last_params == (6, 22, 0, 1, 6)


def test_hourly_graph_equal_from_to_is_invalid(client, monkeypatch):
    """10 -> 10 must stay rejected, not be treated as a 24h range."""
    install_fake_db(monkeypatch)
    resp = client.get("/api/hourly-graph?weekday=2&from_hour=10&to_hour=10")
    assert resp.status_code == 400


def test_hourly_graph_ending_at_midnight_uses_to_hour_24(client, monkeypatch):
    """21:00 -> 00:00 must be sent as to_hour=24 (same-day, non-overnight);
    to_hour=0 is out of range and stays invalid."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/hourly-graph?weekday=2&from_hour=21&to_hour=24")
    assert resp.status_code == 200
    q = conn.cursor_obj.last_query
    assert q.count("weekday = %s") == 1  # same-day branch, not overnight

    resp0 = client.get("/api/hourly-graph?weekday=2&from_hour=21&to_hour=0")
    assert resp0.status_code == 400


def test_hourly_graph_starting_at_midnight(client, monkeypatch):
    """00:00 -> 03:00 stays same-day (from_hour=0 can never exceed to_hour)."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/hourly-graph?weekday=3&from_hour=0&to_hour=3")
    assert resp.status_code == 200
    assert conn.cursor_obj.last_query.count("weekday = %s") == 1
    assert conn.cursor_obj.last_params == (3, 0, 3)


def test_hourly_graph_invalid_hours_out_of_bounds(client, monkeypatch):
    install_fake_db(monkeypatch)
    assert client.get("/api/hourly-graph?weekday=2&from_hour=-1&to_hour=5").status_code == 400
    assert client.get("/api/hourly-graph?weekday=2&from_hour=5&to_hour=25").status_code == 400
    assert client.get("/api/hourly-graph?weekday=2&from_hour=24&to_hour=25").status_code == 400


def test_hourly_graph_chronological_ordering_preserved_end_to_end(client, monkeypatch):
    """Simulates what Postgres would return for an overnight query already
    ordered by the CASE/hour/minute_bucket clause, and confirms the endpoint
    passes that order straight through into the JSON response (no Python-side
    re-sorting that could undo the SQL ordering)."""
    # Rows as the DB would return them, already segment-ordered: 22:00, 23:00
    # (today) then 00:00, 01:00 (tomorrow) — not sorted by raw hour.
    rows = [
        (22, 0, 10.0, 9.0, 11.0, 5, 5),
        (23, 0, 11.0, 10.0, 12.0, 5, 5),
        (0, 0, 8.0, 7.0, 9.0, 5, 5),
        (0, 30, 8.5, 7.5, 9.5, 5, 5),
    ]
    install_fake_db(monkeypatch, rows=rows)
    resp = client.get("/api/hourly-graph?weekday=1&from_hour=22&to_hour=1")
    data = resp.get_json()["data"]
    labels = [d["time_label"] for d in data]
    assert labels == ["22:00", "23:00", "00:00", "00:30"]


# ---------------------------------------------------------------------------
# recommendation()
# ---------------------------------------------------------------------------

def test_recommendation_same_day_unchanged(client, monkeypatch):
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/recommendation?from_hour=10&to_hour=13&allowed_weekdays=0,1")
    assert resp.status_code == 200
    q = conn.cursor_obj.last_query
    assert q.count("ANY(%s)") == 1
    assert conn.cursor_obj.last_params == (
        [0, 1], 10, 13, routes_analytics.MIN_SAMPLE_COUNT_FOR_RECOMMENDATION, routes_analytics.DEFAULT_MAX_RESULTS
    )


def test_recommendation_overnight_single_weekday(client, monkeypatch):
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/recommendation?from_hour=22&to_hour=1&allowed_weekdays=1")
    assert resp.status_code == 200
    q = conn.cursor_obj.last_query
    assert q.count("ANY(%s)") == 2
    assert "LIMIT" in q  # ranking/LIMIT stays in SQL, single query
    weekdays, from_h, next_weekdays, to_h, min_sample, limit = conn.cursor_obj.last_params
    assert weekdays == [1]
    assert from_h == 22
    assert next_weekdays == [2]
    assert to_h == 1


def test_recommendation_multiple_and_consecutive_allowed_weekdays(client, monkeypatch):
    """[1,2] (Tue,Wed): next_weekdays must be the element-wise (w+1)%7 mapping
    [2,3], not some unrelated/flattened set — Wed legitimately appears in both
    lists (as its own late segment AND as Tue's early segment), which is
    correct, not a bug (see report)."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/recommendation?from_hour=22&to_hour=1&allowed_weekdays=1,2")
    assert resp.status_code == 200
    weekdays, _, next_weekdays, *_ = conn.cursor_obj.last_params
    assert weekdays == [1, 2]
    assert next_weekdays == [2, 3]


def test_recommendation_week_boundary_allowed_weekdays(client, monkeypatch):
    """allowed_weekdays including Sunday (6): (6+1)%7 must be 0, not 7."""
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/recommendation?from_hour=22&to_hour=1&allowed_weekdays=6")
    assert resp.status_code == 200
    weekdays, _, next_weekdays, *_ = conn.cursor_obj.last_params
    assert weekdays == [6]
    assert next_weekdays == [0]


def test_recommendation_all_seven_weekdays_overnight(client, monkeypatch):
    conn = install_fake_db(monkeypatch, rows=[])
    resp = client.get("/api/recommendation?from_hour=22&to_hour=1&allowed_weekdays=0,1,2,3,4,5,6")
    assert resp.status_code == 200
    weekdays, _, next_weekdays, *_ = conn.cursor_obj.last_params
    assert set(next_weekdays) == set(weekdays) == {0, 1, 2, 3, 4, 5, 6}


def test_recommendation_equal_from_to_is_invalid(client, monkeypatch):
    install_fake_db(monkeypatch)
    resp = client.get("/api/recommendation?from_hour=10&to_hour=10&allowed_weekdays=0")
    assert resp.status_code == 400


def test_recommendation_ending_at_midnight_and_starting_at_midnight(client, monkeypatch):
    conn = install_fake_db(monkeypatch, rows=[])
    r1 = client.get("/api/recommendation?from_hour=21&to_hour=24&allowed_weekdays=0")
    assert r1.status_code == 200
    assert conn.cursor_obj.last_query.count("ANY(%s)") == 1

    r2 = client.get("/api/recommendation?from_hour=0&to_hour=3&allowed_weekdays=0")
    assert r2.status_code == 200
    assert conn.cursor_obj.last_query.count("ANY(%s)") == 1

    r3 = client.get("/api/recommendation?from_hour=21&to_hour=0&allowed_weekdays=0")
    assert r3.status_code == 400


def test_recommendation_invalid_hours_out_of_bounds(client, monkeypatch):
    install_fake_db(monkeypatch)
    resp = client.get("/api/recommendation?from_hour=-5&to_hour=10&allowed_weekdays=0")
    assert resp.status_code == 400
    resp2 = client.get("/api/recommendation?from_hour=10&to_hour=30&allowed_weekdays=0")
    assert resp2.status_code == 400


def test_recommendation_empty_allowed_weekdays(client, monkeypatch):
    install_fake_db(monkeypatch)
    resp = client.get("/api/recommendation?from_hour=10&to_hour=13&allowed_weekdays=")
    assert resp.status_code == 400
