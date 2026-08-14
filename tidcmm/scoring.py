"""TID-CMM scoring engine.

Implements the weighted rollup, the three integrity constraints (C1 validation
ceiling, C2 visibility ceiling, C3 evidence rule) and the ATT&CK Validated
Coverage Score.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .model import Model

BANDS = [
    (0.00, 0.999, "Level 0 — Absent"),
    (1.00, 1.999, "Level 1 — Ad hoc"),
    (2.00, 2.999, "Level 2 — Repeatable"),
    (3.00, 3.999, "Level 3 — Threat-Informed"),
    (4.00, 4.999, "Level 4 — Measured & Validated"),
    (5.00, 5.000, "Level 5 — Adaptive"),
]

# Coverage scale used by the Validated Coverage Score.
COVERAGE_SCALE = {
    0: "No telemetry",
    1: "Telemetry only",
    2: "Detection logic exists",
    3: "Validated by emulation",
}
COVERAGE_MAX = 3


def evaluate_tiers(model, result, responses: dict[str, "Response"]) -> dict[str, Any]:
    """Which named tier the programme has actually reached.

    A tier requires both the score band and every gate. Score alone can be reached by
    being broadly mediocre; the gates are what make the ladder mean something. The
    blocking gate is reported, because that is the actionable part.
    """
    tiers = model.meta.get("tiers") or []
    if not tiers:
        return {}
    eff: dict[str, int] = {}
    for d in result.domains:
        for row in d.subcapabilities:
            if row["effective_score"] is not None:
                eff[row["id"]] = row["effective_score"]

    achieved, blocked_at, failures = 0, None, []
    for t in sorted(tiers, key=lambda x: x["value"]):
        fails = []
        if result.overall_score < t.get("min_score", 0):
            fails.append({
                "ref": "overall", "required": t.get("min_score"),
                "actual": round(result.overall_score, 2),
                "why": "Weighted overall score below the band for this tier.",
            })
        for g in t.get("gates", []):
            got = eff.get(g["ref"])
            if got is None or got < g["min"]:
                fails.append({
                    "ref": g["ref"], "required": g["min"],
                    "actual": "not scored" if got is None else got,
                    "why": g.get("why", ""),
                })
        if fails:
            blocked_at, failures = t, fails
            break
        achieved = t["value"]

    names = {t["value"]: t["name"] for t in tiers}
    return {
        "achieved": achieved,
        "achieved_name": names.get(achieved, "Below Ad Hoc"),
        "blocked_at": (blocked_at or {}).get("value"),
        "blocked_at_name": (blocked_at or {}).get("name"),
        "failures": failures,
        "summary": (
            f"Tier {achieved} — {names.get(achieved, 'Below Ad Hoc')}"
            + (f". Tier {blocked_at['value']} ({blocked_at['name']}) is blocked by "
               f"{len(failures)} unmet gate{'s' if len(failures) != 1 else ''}."
               if blocked_at else ". Top tier reached.")
        ),
    }


def band_for(score: float) -> str:
    for lo, hi, name in BANDS:
        if lo <= score <= hi:
            return name
    return "Out of range"


@dataclass
class Response:
    """A single sub-capability response."""

    subcapability_id: str
    score: int | None  # None == not applicable / out of scope
    evidence: str = ""
    notes: str = ""
    target: int | None = None
    owner: str = ""


@dataclass
class DomainResult:
    id: str
    name: str
    weight: float
    raw_score: float
    adjusted_score: float
    band: str
    scored: int
    not_applicable: int
    target_score: float | None
    gap_to_target: float | None
    adjustments: list[str] = field(default_factory=list)
    subcapabilities: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AssessmentResult:
    organisation: str
    assessed_on: str
    model_version: str
    strict: bool
    overall_raw: float
    overall_score: float
    overall_band: str
    domains: list[DomainResult]
    constraint_log: list[str]
    coverage: dict[str, Any] | None
    priorities: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "organisation": self.organisation,
            "assessed_on": self.assessed_on,
            "model_version": self.model_version,
            "strict": self.strict,
            "overall_raw": round(self.overall_raw, 2),
            "overall_score": round(self.overall_score, 2),
            "overall_band": self.overall_band,
            "constraint_log": self.constraint_log,
            "coverage": self.coverage,
            "priorities": self.priorities,
            "domains": [
                {
                    "id": d.id,
                    "name": d.name,
                    "weight": d.weight,
                    "raw_score": round(d.raw_score, 2),
                    "score": round(d.adjusted_score, 2),
                    "band": d.band,
                    "scored": d.scored,
                    "not_applicable": d.not_applicable,
                    "target_score": (round(d.target_score, 2) if d.target_score is not None else None),
                    "gap_to_target": (round(d.gap_to_target, 2) if d.gap_to_target is not None else None),
                    "adjustments": d.adjustments,
                    "subcapabilities": d.subcapabilities,
                }
                for d in self.domains
            ],
        }


def _weighted(pairs: Iterable[tuple[float, float]]) -> float:
    pairs = list(pairs)
    tw = sum(w for w, _ in pairs)
    if tw == 0:
        return 0.0
    return sum(w * v for w, v in pairs) / tw


def score_assessment(
    model: Model,
    responses: dict[str, Response],
    *,
    organisation: str = "Unnamed organisation",
    assessed_on: str = "",
    strict: bool = True,
    coverage_rows: list[dict[str, Any]] | None = None,
) -> AssessmentResult:
    """Score a full assessment.

    strict=True applies constraint C3 (unevidenced 4s and 5s are downgraded to 3)
    and constraints C1/C2 (validation and visibility ceilings).
    """
    constraint_log: list[str] = []
    domain_results: list[DomainResult] = []

    # ---- pass 1: sub-capability level, applying C3 -------------------------
    for d in model.domains:
        rows: list[dict[str, Any]] = []
        pairs: list[tuple[float, float]] = []
        tpairs: list[tuple[float, float]] = []
        na = 0
        for s in d.subcapabilities:
            r = responses.get(s.id)
            if r is None or r.score is None:
                na += 1
                rows.append(
                    {
                        "id": s.id,
                        "name": s.name,
                        "weight": s.weight,
                        "score": None,
                        "effective_score": None,
                        "target": None,
                        "evidence": "",
                        "notes": (r.notes if r else ""),
                        "status": "not applicable",
                    }
                )
                continue
            raw = int(r.score)
            eff = raw
            status = "scored"
            if strict and raw >= 4 and not r.evidence.strip():
                eff = 3
                status = "downgraded — no evidence (C3)"
                constraint_log.append(
                    f"C3: {s.id} scored {raw} without named evidence; downgraded to 3."
                )
            pairs.append((s.weight, float(eff)))
            if r.target is not None:
                tpairs.append((s.weight, float(r.target)))
            rows.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "weight": s.weight,
                    "score": raw,
                    "effective_score": eff,
                    "target": r.target,
                    "evidence": r.evidence,
                    "notes": r.notes,
                    "owner": r.owner,
                    "status": status,
                }
            )
        raw_score = _weighted(pairs)
        target_score = _weighted(tpairs) if tpairs else None
        domain_results.append(
            DomainResult(
                id=d.id,
                name=d.name,
                weight=d.weight,
                raw_score=raw_score,
                adjusted_score=raw_score,
                band=band_for(raw_score),
                scored=len(pairs),
                not_applicable=na,
                target_score=target_score,
                gap_to_target=(target_score - raw_score) if target_score is not None else None,
                subcapabilities=rows,
            )
        )

    by_id = {d.id: d for d in domain_results}

    # ---- pass 2: C4 intent ceiling (DC, DE <= max(TI, TM) + 1) -------------
    # Applied before C2 so the causal chain runs strategy -> telemetry ->
    # detection -> validation, each capped by the one it depends on.
    if strict and all(k in by_id for k in ("TI", "TM")):
        intent = max(by_id["TI"].raw_score, by_id["TM"].raw_score)
        cap = intent + 1
        for did in ("DC", "DE"):
            if did in by_id and by_id[did].adjusted_score > cap:
                msg = (
                    f"C4: {did} {by_id[did].adjusted_score:.2f} exceeds max(TI, TM) "
                    f"{intent:.2f} + 1; capped to {cap:.2f}."
                )
                by_id[did].adjusted_score = cap
                by_id[did].adjustments.append(msg)
                constraint_log.append(msg)

    # ---- pass 3: C2 visibility ceiling (DE <= DC + 1) ----------------------
    if strict and "DE" in by_id and "DC" in by_id:
        cap = by_id["DC"].adjusted_score + 1
        if by_id["DE"].raw_score > cap:
            msg = (
                f"C2: DE raw {by_id['DE'].raw_score:.2f} exceeds DC {by_id['DC'].raw_score:.2f} + 1; "
                f"capped to {cap:.2f}."
            )
            by_id["DE"].adjusted_score = cap
            by_id["DE"].adjustments.append(msg)
            constraint_log.append(msg)

    # ---- pass 4: C1 validation ceiling (any domain <= AV + 1) --------------
    if strict and "AV" in by_id:
        cap = by_id["AV"].adjusted_score + 1
        for d in domain_results:
            if d.id == "AV":
                continue
            if d.adjusted_score > cap:
                msg = (
                    f"C1: {d.id} {d.adjusted_score:.2f} exceeds AV {by_id['AV'].adjusted_score:.2f} + 1; "
                    f"capped to {cap:.2f}."
                )
                d.adjusted_score = cap
                d.adjustments.append(msg)
                constraint_log.append(msg)

    for d in domain_results:
        d.band = band_for(d.adjusted_score)
        if d.target_score is not None:
            d.gap_to_target = d.target_score - d.adjusted_score

    overall_raw = _weighted((d.weight, d.raw_score) for d in domain_results)
    overall = _weighted((d.weight, d.adjusted_score) for d in domain_results)

    coverage = compute_coverage(coverage_rows) if coverage_rows else None
    priorities = build_priorities(model, domain_results)

    return AssessmentResult(
        organisation=organisation,
        assessed_on=assessed_on,
        model_version=model.meta["model"]["version"],
        strict=strict,
        overall_raw=overall_raw,
        overall_score=overall,
        overall_band=band_for(overall),
        domains=domain_results,
        constraint_log=constraint_log,
        coverage=coverage,
        priorities=priorities,
    )


def compute_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Validated Coverage Score over in-scope ATT&CK techniques.

    Each row: {technique_id, name, tactics, in_scope (bool), status (0-3)}
    """
    inscope = [r for r in rows if r.get("in_scope")]
    if not inscope:
        return {"in_scope": 0, "vcs_percent": 0.0, "distribution": {}, "by_tactic": {}}
    total = sum(int(r.get("status", 0)) for r in inscope)
    vcs = 100.0 * total / (COVERAGE_MAX * len(inscope))
    dist = {label: 0 for label in COVERAGE_SCALE.values()}
    for r in inscope:
        dist[COVERAGE_SCALE[int(r.get("status", 0))]] += 1
    by_tactic: dict[str, dict[str, float]] = {}
    for r in inscope:
        for t in str(r.get("tactics", "")).split(";"):
            t = t.strip()
            if not t:
                continue
            b = by_tactic.setdefault(t, {"count": 0, "points": 0})
            b["count"] += 1
            b["points"] += int(r.get("status", 0))
    for t, b in by_tactic.items():
        b["vcs_percent"] = round(100.0 * b["points"] / (COVERAGE_MAX * b["count"]), 1)
    return {
        "in_scope": len(inscope),
        "assessed_total": len(rows),
        "vcs_percent": round(vcs, 1),
        "detected_or_better_percent": round(
            100.0 * sum(1 for r in inscope if int(r.get("status", 0)) >= 2) / len(inscope), 1
        ),
        "validated_percent": round(
            100.0 * sum(1 for r in inscope if int(r.get("status", 0)) >= 3) / len(inscope), 1
        ),
        "distribution": dist,
        "by_tactic": by_tactic,
    }


def build_priorities(model: Model, results: list[DomainResult], limit: int = 12) -> list[dict[str, Any]]:
    """Rank improvement actions by (domain weight x sub-capability weight x gap)."""
    items: list[dict[str, Any]] = []
    dmap = {d.id: d for d in model.domains}
    for dr in results:
        for row in dr.subcapabilities:
            if row["effective_score"] is None:
                continue
            target = row["target"] if row["target"] is not None else min(row["effective_score"] + 1, 5)
            gap = target - row["effective_score"]
            if gap <= 0:
                continue
            sub = next(s for s in dmap[dr.id].subcapabilities if s.id == row["id"])
            impact = (dr.weight / 100) * (row["weight"] / 100) * gap
            items.append(
                {
                    "subcapability_id": row["id"],
                    "domain": dr.id,
                    "name": row["name"],
                    "current": row["effective_score"],
                    "target": target,
                    "gap": gap,
                    "impact": round(impact * 1000, 2),
                    "next_level_action": sub.levels.get(min(row["effective_score"] + 1, 5), ""),
                    "evidence_required": sub.evidence,
                    "owner": row.get("owner", ""),
                }
            )
    items.sort(key=lambda x: (-x["impact"], x["subcapability_id"]))
    return items[:limit]
