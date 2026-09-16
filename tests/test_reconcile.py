from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reconcile import (
    FieldObservation,
    reconcile_account,
    score_confidence,
)


def test_most_recent_value_wins():
    obs = {
        "email": [
            FieldObservation("hubspot", "old@acme.io", "2024-01-01T00:00:00"),
            FieldObservation("salesforce", "new@acme.io", "2024-06-01T00:00:00"),
        ]
    }
    result = reconcile_account(obs, match_signals=["exact_email"])
    assert result.values["email"] == "new@acme.io"


def test_source_priority_breaks_timestamp_tie():
    ts = "2024-06-01T00:00:00"
    obs = {
        "phone": [
            FieldObservation("hubspot", "111", ts),
            FieldObservation("enrichment", "999", ts),
        ]
    }
    result = reconcile_account(obs, match_signals=["phone"])
    assert result.values["phone"] == "999"


def test_exact_email_scores_higher_than_phone_only():
    email_conf = score_confidence(["salesforce"], ["exact_email"])
    phone_conf = score_confidence(["salesforce"], ["phone"])
    assert email_conf > phone_conf


def test_corroboration_bumps_confidence_and_clamps():
    single = score_confidence(["salesforce"], ["domain_company"])
    multi = score_confidence(
        ["salesforce", "hubspot", "enrichment"], ["domain_company"]
    )
    assert multi > single
    assert score_confidence(["a", "b", "c", "d"], ["exact_email"]) <= 1.0
