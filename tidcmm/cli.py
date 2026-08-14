"""TID-CMM command line interface.

    python -m tidcmm validate
    python -m tidcmm export-json build/model.json
    python -m tidcmm score assessments/example-assessment.yaml -o report.json
    python -m tidcmm template my-assessment.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

from .model import MODEL_DIR, export_json, load_model, validate_model
from .scoring import Response, score_assessment

ROOT = Path(__file__).resolve().parent.parent


def _load_responses(path: Path):
    data = yaml.safe_load(path.read_text())
    responses = {}
    for sid, raw in (data.get("responses") or {}).items():
        if isinstance(raw, dict):
            responses[sid] = Response(
                subcapability_id=sid,
                score=raw.get("score"),
                evidence=str(raw.get("evidence", "") or ""),
                notes=str(raw.get("notes", "") or ""),
                target=raw.get("target"),
                owner=str(raw.get("owner", "") or ""),
            )
        else:
            responses[sid] = Response(subcapability_id=sid, score=raw)
    return data, responses


def cmd_validate(args):
    model = load_model(args.model_dir)
    errors = validate_model(model)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    subs = model.subcapabilities()
    print(
        f"OK — {model.meta['model']['id']} v{model.meta['model']['version']}: "
        f"{len(model.domains)} domains, {len(subs)} sub-capabilities, "
        f"{len(subs) * 6} level descriptors."
    )
    return 0


def cmd_export_json(args):
    model = load_model(args.model_dir)
    p = export_json(model, args.output)
    print(f"Wrote {p}")
    return 0


def cmd_template(args):
    model = load_model(args.model_dir)
    lines = [
        "# TID-CMM assessment template",
        f"# Model version: {model.meta['model']['version']}",
        "organisation: \"\"",
        f"assessed_on: \"{date.today().isoformat()}\"",
        "assessor: \"\"",
        "scope: \"\"",
        "strict: true",
        "responses:",
    ]
    for d in model.domains:
        lines.append(f"  # ---- {d.id}: {d.name} (weight {d.weight}%) ----")
        for s in d.subcapabilities:
            lines.append(f"  # {s.question}")
            lines.append(f"  {s.id}:")
            lines.append("    score: 0        # 0-5 or null for not applicable")
            lines.append("    target: 3       # desired level")
            lines.append("    evidence: \"\"    # required for a score of 4 or 5")
            lines.append("    owner: \"\"")
            lines.append("    notes: \"\"")
    Path(args.output).write_text("\n".join(lines) + "\n")
    print(f"Wrote {args.output}")
    return 0


def cmd_score(args):
    model = load_model(args.model_dir)
    data, responses = _load_responses(Path(args.assessment))
    coverage_rows = None
    if args.coverage:
        import csv

        with open(args.coverage, newline="") as f:
            coverage_rows = [
                {
                    "technique_id": r["technique_id"],
                    "name": r.get("name", ""),
                    "tactics": r.get("tactics", ""),
                    "in_scope": str(r.get("in_scope", "")).strip().lower() in ("1", "true", "yes", "y"),
                    "status": int(r.get("status", 0) or 0),
                }
                for r in csv.DictReader(f)
            ]
    result = score_assessment(
        model,
        responses,
        organisation=data.get("organisation", "Unnamed organisation"),
        assessed_on=str(data.get("assessed_on", "")),
        strict=data.get("strict", True) if args.strict is None else args.strict,
        coverage_rows=coverage_rows,
    )
    out = result.to_dict()
    if args.output:
        Path(args.output).write_text(json.dumps(out, indent=2))
        print(f"Wrote {args.output}")
    _print_report(out)
    return 0


def _bar(v: float, width: int = 20) -> str:
    filled = int(round(v / 5 * width))
    return "█" * filled + "·" * (width - filled)


def _print_report(out: dict) -> None:
    print()
    print("=" * 72)
    print(f"TID-CMM assessment — {out['organisation']}  ({out['assessed_on']})")
    print("=" * 72)
    for d in out["domains"]:
        flag = " *" if d["adjustments"] else ""
        print(f"  {d['id']:3} {d['name'][:44]:44} {_bar(d['score'])} {d['score']:.2f}{flag}")
    print("-" * 72)
    print(f"  OVERALL: {out['overall_score']:.2f}  ({out['overall_band']})")
    if out["overall_raw"] != out["overall_score"]:
        print(f"  Unadjusted self-assessed score was {out['overall_raw']:.2f}.")
    if out["coverage"]:
        c = out["coverage"]
        print(
            f"  ATT&CK Validated Coverage Score: {c['vcs_percent']}%  "
            f"({c['in_scope']} techniques in scope, {c['validated_percent']}% validated)"
        )
    if out["constraint_log"]:
        print("\n  Integrity constraints applied:")
        for line in out["constraint_log"]:
            print(f"    - {line}")
    print("\n  Top improvement priorities (weighted impact):")
    for p in out["priorities"][:8]:
        print(f"    [{p['impact']:5.1f}] {p['subcapability_id']:6} {p['name'][:46]:46} {p['current']} -> {p['target']}")
    print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tidcmm", description="TID-CMM model tooling")
    ap.add_argument("--model-dir", default=str(MODEL_DIR))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate").set_defaults(func=cmd_validate)

    p = sub.add_parser("export-json")
    p.add_argument("output", nargs="?", default=str(ROOT / "build" / "model.json"))
    p.set_defaults(func=cmd_export_json)

    p = sub.add_parser("template")
    p.add_argument("output", nargs="?", default="assessment.yaml")
    p.set_defaults(func=cmd_template)

    p = sub.add_parser("score")
    p.add_argument("assessment")
    p.add_argument("-o", "--output")
    p.add_argument("--coverage", help="CSV of ATT&CK coverage rows")
    p.add_argument("--strict", dest="strict", action="store_true", default=None)
    p.add_argument("--no-strict", dest="strict", action="store_false")
    p.set_defaults(func=cmd_score)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
