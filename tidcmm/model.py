"""TID-CMM model loading and validation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import yaml

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
LEVEL_VALUES = [0, 1, 2, 3, 4, 5]


@dataclass
class SubCapability:
    id: str
    name: str
    weight: float
    question: str
    levels: dict[int, str]
    evidence: list[str] = field(default_factory=list)
    crosswalk: dict[str, list[str]] = field(default_factory=dict)
    attack_link: str | None = None
    profile: str = "comprehensive"
    domain_id: str = ""


@dataclass
class Domain:
    id: str
    name: str
    weight: float
    intent: str
    anti_pattern: str | None
    ceiling_rule: str | None
    subcapabilities: list[SubCapability]


@dataclass
class Model:
    meta: dict[str, Any]
    domains: list[Domain]

    @property
    def levels(self) -> list[dict[str, Any]]:
        return self.meta["levels"]

    def domain(self, did: str) -> Domain:
        for d in self.domains:
            if d.id == did:
                return d
        raise KeyError(did)

    def subcapabilities(self) -> list[SubCapability]:
        return [s for d in self.domains for s in d.subcapabilities]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.meta["model"],
            "alignment": self.meta["alignment"],
            "levels": self.meta["levels"],
            "scoring": self.meta["scoring"],
            "domains": [
                {
                    "id": d.id,
                    "name": d.name,
                    "weight": d.weight,
                    "intent": d.intent.strip(),
                    "anti_pattern": (d.anti_pattern or "").strip() or None,
                    "ceiling_rule": (d.ceiling_rule or "").strip() or None,
                    "subcapabilities": [asdict(s) for s in d.subcapabilities],
                }
                for d in self.domains
            ],
        }


def load_model(model_dir: Path | str = MODEL_DIR) -> Model:
    model_dir = Path(model_dir)
    meta = yaml.safe_load((model_dir / "meta.yaml").read_text())
    domains: list[Domain] = []
    for entry in meta["domains"]:
        raw = yaml.safe_load((model_dir / entry["file"]).read_text())
        d = raw["domain"]
        subs = []
        for s in raw["subcapabilities"]:
            subs.append(
                SubCapability(
                    id=s["id"],
                    name=s["name"],
                    weight=float(s["weight"]),
                    question=" ".join(s["question"].split()),
                    levels={int(k): " ".join(str(v).split()) for k, v in s["levels"].items()},
                    evidence=s.get("evidence", []),
                    crosswalk=s.get("crosswalk", {}),
                    attack_link=(" ".join(s["attack_link"].split()) if s.get("attack_link") else None),
                    profile=s.get("profile", "comprehensive"),
                    domain_id=d["id"],
                )
            )
        domains.append(
            Domain(
                id=d["id"],
                name=d["name"],
                weight=float(d["weight"]),
                intent=d.get("intent", ""),
                anti_pattern=d.get("anti_pattern"),
                ceiling_rule=d.get("ceiling_rule"),
                subcapabilities=subs,
            )
        )
    return Model(meta=meta, domains=domains)


def validate_model(model: Model) -> list[str]:
    """Return a list of validation errors. Empty list means the model is valid."""
    errors: list[str] = []
    total = sum(d.weight for d in model.domains)
    if abs(total - 100) > 1e-6:
        errors.append(f"Domain weights sum to {total}, expected 100")
    seen: set[str] = set()
    for d in model.domains:
        sw = sum(s.weight for s in d.subcapabilities)
        if abs(sw - 100) > 1e-6:
            errors.append(f"{d.id}: sub-capability weights sum to {sw}, expected 100")
        if not d.subcapabilities:
            errors.append(f"{d.id}: no sub-capabilities")
        for s in d.subcapabilities:
            if s.id in seen:
                errors.append(f"Duplicate sub-capability id {s.id}")
            seen.add(s.id)
            if not s.id.startswith(d.id + "."):
                errors.append(f"{s.id}: id does not match domain prefix {d.id}")
            missing = [lv for lv in LEVEL_VALUES if lv not in s.levels]
            if missing:
                errors.append(f"{s.id}: missing level descriptors {missing}")
            for lv, text in s.levels.items():
                if not text or len(text) < 15:
                    errors.append(f"{s.id}: level {lv} descriptor is empty or too short")
            if not s.question.endswith("?"):
                errors.append(f"{s.id}: question does not end with '?'")
            if not s.evidence:
                errors.append(f"{s.id}: no evidence examples defined")
    return errors


def export_json(model: Model, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model.to_dict(), indent=2, ensure_ascii=False))
    return path
