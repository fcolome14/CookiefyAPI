import pytest
from datetime import datetime, timedelta, timezone
from app.schemas.post import ListKPIs, SiteKPIs
from app.algorithms.algorithm import Score

def utc_days_ago(days):
    return datetime.now(timezone.utc) - timedelta(days=days)

@pytest.fixture
def score_service():
    return Score()

import pytest
from datetime import datetime, timedelta, timezone
from app.schemas.post import ListKPIs

# Helper
def utc_days_ago(days):
    return datetime.now(timezone.utc) - timedelta(days=days)

@pytest.mark.parametrize(
    "likes, visit_count, shares, saves, image, created_at, expected_score",
    [
        (20, 100, 10, 5, 12, utc_days_ago(5), 23.99001),
        (20, 100, 10, 5, 1,  utc_days_ago(2), 21.72284),
        (0, 0, 0, 0, 1,      utc_days_ago(1), 0.0),
        (50, 200, 30, 20, 12, utc_days_ago(10), 67.07799),
        (10, 50, 5, 2, 1,    utc_days_ago(1), 10.58514),
        (100, 500, 50, 25, 12, utc_days_ago(0.5), 121.18283),
        (0, 0, 0, 0, 12,     utc_days_ago(30), 0.0),
    ]
)
def test_compute_list_score_with_image(score_service, likes, visit_count, shares, saves, image, created_at, expected_score):
    kpis = ListKPIs(
        id=1,
        likes=likes,
        visit_count=visit_count,
        shares=shares,
        saves=saves,
        image=image,
        created_at=created_at,
    )
    result = score_service.compute_list_score(kpis)
    print(f"Computed score for likes={likes}, visit_count={visit_count} → {result}")
    assert isinstance(result, float)
    assert round(result, 5) == pytest.approx(expected_score, abs=1e-4)


@pytest.mark.parametrize(
    "visit_count, list_count, expected_score",
    [
    (0, 0, 0),
    (100, 10, 0.2),
    (200, 15, 0.325),
    (50, 5, 0.1),
    (300, 30, 0.6),
    (150, 20, 0.375),
    (0, 5, 0.075),
    (1000, 100, 2.0),
    (500, 50, 1.0),
    (250, 25, 0.5),
    (75, 7, 0.1425),
    ]
)
def test_compute_site_score(score_service, visit_count, list_count, expected_score):
    kpis = SiteKPIs(
        click_count=visit_count,
        lists_count=list_count
    )
    result = score_service.compute_site_score(kpis)
    print(f"Computed score for list_count={list_count}, visit_count={visit_count} → {result}")
    assert isinstance(result, float)
    assert round(result, 5) == pytest.approx(expected_score, abs=1e-4)
