from __future__ import annotations

"""Field-level reconciliation and confidence scoring for canonical accounts.

When the same account is seen across multiple CRMs (Salesforce, HubSpot) and
enrichment APIs, each source proposes values for the same fields. This module
picks the winning value per field and produces a defensible confidence score,
driven by the weights in ``configs/identity.yaml``.
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Source trust priority when timestamps tie. Higher wins.
SOURCE_PRIORITY = {
    "enrichment": 3,
    "salesforce": 2,
    "hubspot": 1,
}


@dataclass
class FieldObservation:
    source: str
    value: str | None
    updated_at: str | None = None


@dataclass
class ReconcileResult:
    values: dict[str, str | None] = field(default_factory=dict)
    confidence: float = 0.0
    match_signals: list[str] = field(default_factory=list)


def load_rule_weights(config_path: Path | None = None) -> dict[str, float]:
    path = config_path or (
        Path(__file__).resolve().parents[1] / "configs" / "identity.yaml"
    )
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {rule["name"]: float(rule["weight"]) for rule in config.get("rules", [])}


def _pick_value(observations: list[FieldObservation]) -> str | None:
    """Most-recent-wins, tie-broken by source priority."""
    candidates = [o for o in observations if o.value]
    if not candidates:
        return None
    candidates.sort(
        key=lambda o: (o.updated_at or "", SOURCE_PRIORITY.get(o.source, 0)),
        reverse=True,
    )
    return candidates[0].value


def score_confidence(
    sources: list[str],
    match_signals: list[str],
    weights: dict[str, float] | None = None,
) -> float:
    """Blend match-signal strength with cross-source corroboration.

    - A strong signal (exact_email weight 1.0) anchors the base score.
    - Each additional corroborating source adds a small bump.
    - Score is clamped to [0, 1] so it can be surfaced as an SLA gate.
    """
    weights = weights or load_rule_weights()
    base = max((weights.get(sig, 0.0) for sig in match_signals), default=0.4)
    corroboration = 0.1 * max(0, len(set(sources)) - 1)
    return round(min(1.0, base + corroboration), 3)


def reconcile_account(
    field_observations: dict[str, list[FieldObservation]],
    match_signals: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> ReconcileResult:
    match_signals = match_signals or []
    values = {name: _pick_value(obs) for name, obs in field_observations.items()}
    sources = sorted(
        {o.source for obs in field_observations.values() for o in obs if o.value}
    )
    confidence = score_confidence(sources, match_signals, weights)
    return ReconcileResult(
        values=values, confidence=confidence, match_signals=match_signals
    )
