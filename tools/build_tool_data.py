"""Build the compact data payload the browser tool embeds.

Integer-indexed to keep the single-file tool small enough to load instantly.

    python tools/build_tool_data.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tidcmm.model import load_model  # noqa: E402
from tidcmm.scoping import LOG_SOURCE_MAP, OS_INSTRUMENTED, OS_SOURCES, PLATFORM_MAP  # noqa: E402

DATA = ROOT / "data"
OUT = ROOT / "build" / "tool_data.json"


def build() -> dict:
    model = load_model()

    with open(DATA / "attack_techniques.csv", newline="") as f:
        techs = list(csv.DictReader(f))
    tid_index = {t["technique_id"]: i for i, t in enumerate(techs)}

    tactics: list[str] = []
    platforms: list[str] = []

    def idx(pool: list[str], v: str) -> int:
        if v not in pool:
            pool.append(v)
        return pool.index(v)

    T = []
    for t in techs:
        T.append({
            "i": t["technique_id"],
            "n": t["name"],
            "s": t["is_subtechnique"] == "Yes",
            "t": [idx(tactics, x.strip()) for x in t["tactics"].split(";") if x.strip()],
            "p": [idx(platforms, x.strip()) for x in t["platforms"].split(";") if x.strip()],
        })

    # Groups and campaigns only. Malware and tools are reachable through the groups
    # that use them, and including 825 of them would triple the payload.
    A = []
    with open(DATA / "attack_actors.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["kind"] not in ("group", "campaign"):
                continue
            ids = [tid_index[x] for x in r["techniques"].split() if x in tid_index]
            if not ids:
                continue
            A.append({
                "i": r["attack_id"], "n": r["name"], "k": r["kind"],
                "a": r["aliases"], "c": len(ids), "t": ids,
            })
    A.sort(key=lambda x: (-x["c"], x["n"]))

    sources: list[str] = []
    AN = []
    raw = json.loads((DATA / "attack_analytics.json").read_text())["analytics"]
    for a in raw:
        if a["t"] not in tid_index:
            continue
        AN.append({
            "t": tid_index[a["t"]],
            "p": [idx(platforms, x) for x in a.get("p", [])],
            "s": [idx(sources, x) for x in a["s"]],
        })

    catalogue = yaml.safe_load((DATA / "telemetry_catalogue.yaml").read_text())["sources"]
    cat = {}
    for name, info in catalogue.items():
        cat[name] = {
            "what": " ".join(str(info.get("what", "")).split()),
            "ch": info.get("key_channels", ""),
            "how": " ".join(str(info.get("how", "")).split()),
            "tool": info.get("tool_class", ""),
            "free": info.get("open_source", ""),
            "effort": info.get("effort", ""),
            "volume": info.get("volume", ""),
        }

    return {
        "model": model.to_dict(),
        "tiers": model.meta.get("tiers", []),
        "profiles": model.meta.get("profiles", {}),
        "classes": model.meta.get("detection_classes", {}),
        "archetypes": model.meta.get("environment_archetypes", {}),
        "tactics": tactics,
        "platforms": platforms,
        "sources": sources,
        "techniques": T,
        "actors": A,
        "analytics": AN,
        "catalogue": cat,
        "maps": {
            "log_source": LOG_SOURCE_MAP,
            "os_sources": OS_SOURCES,
            "os_instrumented": OS_INSTRUMENTED,
            "platform": {k: {kk: sorted(vv) for kk, vv in v.items()} for k, v in PLATFORM_MAP.items()},
        },
    }


if __name__ == "__main__":
    d = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
    print(f"{OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    print(f"  techniques {len(d['techniques'])} · actors {len(d['actors'])} · "
          f"analytics {len(d['analytics'])} · sources {len(d['sources'])} · "
          f"catalogued {len(d['catalogue'])}")
