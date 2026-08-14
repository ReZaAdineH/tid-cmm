"""TID-CMM scoping and detectability engine.

Implements the sequence the model argues for:

    environment  ->  crown jewels  ->  threat profile  ->  attack trees
                            |
                            v
              derived in-scope ATT&CK set (an intersection, not a selection)

and the telemetry advisory: given what an organisation actually collects, which of
ATT&CK's own published detection analytics it is able to execute at all.

Uses ATT&CK v19 detection objects (detection strategies and analytics), whose
log source references name concrete channels — so "you have no Sysmon" becomes a
computed number rather than a caveat.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

DATA = Path(__file__).resolve().parent.parent / "data"

# ---------------------------------------------------------------------------
# Environment declaration -> reachable ATT&CK log sources.
#
# Prefix-matched against the 266 log source names ATT&CK v19 references from its
# analytics. Deliberately expressed as capabilities, not products: an EDR and a
# well-configured open-source stack reach overlapping sets, and the model says so.
# ---------------------------------------------------------------------------
OS_SOURCES = {
    "windows": ["WinEventLog:Security", "WinEventLog:System", "WinEventLog:Application",
                "WinEventLog:PowerShell"],
    "linux": ["linux:syslog"],
    "macos": ["macos:unifiedlog"],
}
OS_INSTRUMENTED = {
    "windows": {"open-source-instrumentation": ["WinEventLog:Sysmon"],
                "commercial-edr": ["WinEventLog:Sysmon", "etw:"]},
    "linux": {"open-source-instrumentation": ["linux:Sysmon", "auditd:", "linux:osquery"],
              "commercial-edr": ["linux:Sysmon", "auditd:"]},
    "macos": {"open-source-instrumentation": ["macos:osquery"],
              "commercial-edr": ["macos:endpointsecurity", "macos:osquery"]},
}
NATIVE_OS: list[str] = []
LOG_SOURCE_MAP: dict[str, dict[str, list[str]]] = {
    "endpoint_telemetry": {
        # An EDR supplies process, command line, module load and file telemetry
        # equivalent to the Sysmon-referenced analytics, plus kernel-level sources.
        "commercial-edr": NATIVE_OS + [
            "WinEventLog:Sysmon", "linux:Sysmon", "etw:", "auditd:",
            "macos:endpointsecurity", "fs:fsusage", "esxi:",
        ],
        "open-source-instrumentation": NATIVE_OS + [
            "WinEventLog:Sysmon", "linux:Sysmon", "auditd:",
            "linux:osquery", "macos:osquery", "fs:fsusage", "esxi:",
        ],
        "native-os-logging-only": NATIVE_OS,
        "none": [],
    },
    "network_telemetry": {
        "inline-inspection": ["NSM:", "Network Traffic", "Domain Name", "networkdevice:"],
        "passive-sensor": ["NSM:Flow", "NSM:Connections", "Network Traffic", "Domain Name"],
        "flow-only": ["NSM:Flow"],
        "none": [],
    },
    "cloud": {
        "aws": ["AWS:"], "azure": ["azure:"], "gcp": ["gcp:"], "other": [], "none": [],
    },
    "productivity": {
        "microsoft-365": ["m365:"], "google-workspace": ["gworkspace:", "google:"],
        "other": [], "none": [],
    },
    "identity": {
        "active-directory": ["WinEventLog:Security"],
        "entra-id": ["azure:signinlogs", "azure:audit", "m365:signinlogs"],
        "okta": ["saas:okta"],
        "other-idp": ["saas:"], "none": [],
    },
    "workload": {
        "containers": ["kubernetes:", "docker:"],
        "servers": [], "serverless": [], "mainframe": [], "none": [],
    },
}

# Profile derivation. Deliberately conservative: the burden of the full model is
# only imposed where the estate and operating model justify it.
_COMPLEX = {"estate": {"hybrid", "cloud-native", "ot-ics", "developer-platform"}}


@dataclass
class Environment:
    # Which operating systems are actually run. Inferring these from the estate type
    # produced advice about macOS to organisations with no Macs, so it is now asked.
    windows: bool = True
    linux: bool = False
    macos: bool = False
    estate: str = "on-premises"
    cloud: str = "none"
    productivity: str = "none"
    identity: str = "active-directory"
    endpoint_telemetry: str = "native-os-logging-only"
    network_telemetry: str = "none"
    workload: str = "servers"
    operating_model: str = "no-soc"
    regulated: bool = False
    size: str = "small"  # small | medium | large

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ScopeResult:
    in_scope: dict[str, str]           # technique_id -> tier A/B/C
    tier_counts: dict[str, int]
    total_techniques: int
    notices: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.in_scope)


def _load_techniques() -> list[dict[str, str]]:
    with open(DATA / "attack_techniques.csv", newline="") as f:
        return list(csv.DictReader(f))


def _load_analytics() -> list[dict[str, Any]]:
    return json.loads((DATA / "attack_analytics.json").read_text())["analytics"]


def analytics_for(env: "Environment") -> list[dict[str, Any]]:
    """Analytics that could apply to this estate.

    A cross-platform technique carries analytics for every platform it affects. An
    all-Windows estate must not be advised to collect macOS unified logs merely
    because the technique also runs on macOS, so analytics are filtered by platform.
    """
    plats = platforms_for(env)
    out = []
    for a in _load_analytics():
        ap = a.get("p") or []
        if not ap or (set(ap) & plats):
            out.append(a)
    return out


def _load_actors() -> dict[str, dict[str, Any]]:
    out = {}
    with open(DATA / "attack_actors.csv", newline="") as f:
        for r in csv.DictReader(f):
            r["techniques"] = r["techniques"].split()
            out[r["attack_id"]] = r
    return out


# ---------------------------------------------------------------------------
# Profile derivation
# ---------------------------------------------------------------------------
def derive_profile(env: Environment) -> str:
    """Derive the applicability profile from the declared environment."""
    if env.operating_model == "no-soc" and env.size == "small" and not env.regulated:
        return "essential"
    score = 0
    score += 2 if env.operating_model == "in-house-soc" else 1 if env.operating_model == "hybrid-mssp" else 0
    score += 1 if env.estate in _COMPLEX["estate"] else 0
    score += 1 if env.cloud != "none" else 0
    score += 1 if env.regulated else 0
    score += 1 if env.size == "large" else 0
    if score >= 5:
        return "comprehensive"
    if score >= 2:
        return "standard"
    return "essential"


def challenge_profile(env: Environment, chosen: str) -> str | None:
    """Return a notice if the chosen profile is implausible for the environment.

    Never blocks. The notice is recorded in the report, not only shown on screen.
    """
    derived = derive_profile(env)
    order = {"essential": 0, "standard": 1, "comprehensive": 2}
    if order.get(chosen, 0) >= order[derived]:
        return None
    return (
        f"Profile challenge: you selected '{chosen}' but the declared environment derives "
        f"'{derived}' ({env.operating_model}, {env.estate} estate, "
        f"cloud={env.cloud}, regulated={env.regulated}, size={env.size}). "
        f"Assessing at a narrower profile than your environment warrants means the score "
        f"is not comparable with peers assessed at '{derived}', and the sub-capabilities "
        f"excluded are not marked as risks accepted. Record a rationale."
    )


# ---------------------------------------------------------------------------
# Telemetry reachability
# ---------------------------------------------------------------------------
def operating_systems(env: Environment) -> list[str]:
    return [os for os in ("windows", "linux", "macos") if getattr(env, os, False)]


def reachable_sources(env: Environment) -> list[str]:
    """Log source name prefixes the declared environment can actually produce.

    Endpoint sources are gated on the operating systems actually run, so an
    all-Windows estate is never told to collect macOS unified logs.
    """
    prefixes: set[str] = set()
    for dim, options in LOG_SOURCE_MAP.items():
        if dim == "endpoint_telemetry":
            continue
        prefixes.update(options.get(getattr(env, dim, "none"), []))
    tier = env.endpoint_telemetry
    if tier != "none":
        for os_name in operating_systems(env):
            prefixes.update(OS_SOURCES[os_name])
            prefixes.update(OS_INSTRUMENTED[os_name].get(tier, []))
    if tier in ("open-source-instrumentation", "commercial-edr"):
        prefixes.update(["fs:fsusage", "esxi:"])
    return sorted(prefixes)


def _reaches(source: str, prefixes: Iterable[str]) -> bool:
    return any(source.startswith(p) for p in prefixes)


def detectability(env: Environment, technique_ids: Iterable[str] | None = None) -> dict[str, Any]:
    """For each technique, how many of ATT&CK's own analytics you could execute.

    An analytic counts as reachable when at least one of its referenced log sources
    is reachable in the declared environment. That is deliberately generous — it
    says the analytic is *implementable*, not that it is implemented.
    """
    prefixes = reachable_sources(env)
    analytics = analytics_for(env)
    wanted = set(technique_ids) if technique_ids is not None else None

    per: dict[str, dict[str, int]] = {}
    for a in analytics:
        if wanted is not None and a["t"] not in wanted:
            continue
        rec = per.setdefault(a["t"], {"total": 0, "reachable": 0})
        rec["total"] += 1
        if any(_reaches(s, prefixes) for s in a["s"]):
            rec["reachable"] += 1

    blind = [t for t, r in per.items() if r["reachable"] == 0]
    partial = [t for t, r in per.items() if 0 < r["reachable"] < r["total"]]
    full = [t for t, r in per.items() if r["reachable"] == r["total"] and r["total"] > 0]
    return {
        "reachable_source_prefixes": prefixes,
        "per_technique": per,
        "blind": sorted(blind),
        "partial": sorted(partial),
        "full": sorted(full),
        "assessed": len(per),
        "blind_percent": round(100 * len(blind) / len(per), 1) if per else 0.0,
    }


def missing_sources(env: Environment, technique_ids: Iterable[str]) -> list[tuple[str, int]]:
    """Log sources that would unblock the most in-scope techniques, ranked.

    Names capabilities ATT&CK itself references. It never recommends a product.
    """
    prefixes = reachable_sources(env)
    wanted = set(technique_ids)
    gain: dict[str, set[str]] = {}
    for a in analytics_for(env):
        if a["t"] not in wanted:
            continue
        if any(_reaches(s, prefixes) for s in a["s"]):
            continue  # already reachable
        for s in a["s"]:
            gain.setdefault(s, set()).add(a["t"])
    return sorted(((s, len(t)) for s, t in gain.items()), key=lambda x: -x[1])


# ---------------------------------------------------------------------------
# In-scope derivation: the intersection
# ---------------------------------------------------------------------------
PLATFORM_MAP = {
    "estate": {
        "on-premises": {"Windows", "Linux", "macOS", "Network Devices", "ESXi"},
        "hybrid": {"Windows", "Linux", "macOS", "Network Devices", "ESXi", "IaaS", "SaaS", "Identity Provider"},
        "cloud-native": {"Linux", "IaaS", "SaaS", "Containers", "Identity Provider"},
        "saas-only": {"SaaS", "Office Suite", "Identity Provider"},
        "ot-ics": {"Windows", "Linux", "Network Devices"},
        "developer-platform": {"Linux", "Containers", "IaaS"},
    },
    "cloud": {"aws": {"IaaS"}, "azure": {"IaaS", "Identity Provider"}, "gcp": {"IaaS"},
              "other": {"IaaS"}, "none": set()},
    "productivity": {"microsoft-365": {"Office Suite", "SaaS"},
                     "google-workspace": {"Office Suite", "SaaS"}, "other": {"SaaS"}, "none": set()},
    "identity": {"active-directory": {"Windows"}, "entra-id": {"Identity Provider"},
                 "okta": {"Identity Provider"}, "other-idp": {"Identity Provider"}, "none": set()},
    "workload": {"containers": {"Containers"}, "servers": set(), "serverless": {"IaaS"},
                 "mainframe": set(), "none": set()},
}


OS_PLATFORM = {"windows": "Windows", "linux": "Linux", "macos": "macOS"}


def platforms_for(env: Environment) -> set[str]:
    """ATT&CK platforms in scope. Operating systems come from the explicit
    declaration; everything else from the estate and service declarations."""
    plats: set[str] = {OS_PLATFORM[o] for o in operating_systems(env)}
    for dim, options in PLATFORM_MAP.items():
        if dim == "estate":
            continue  # estate no longer implies an operating system
        plats |= options.get(getattr(env, dim, "none"), set())
    if env.estate in ("on-premises", "hybrid"):
        plats |= {"Network Devices", "ESXi"}
    if env.estate in ("hybrid", "cloud-native", "developer-platform"):
        plats |= {"IaaS"}
    if env.estate in ("saas-only", "hybrid"):
        plats |= {"SaaS", "Office Suite"}
    plats.add("PRE")
    return plats


def derive_scope(
    env: Environment,
    actor_ids: Iterable[str] = (),
    tree_techniques: Iterable[str] = (),
    *,
    include_unattributed_on_path: bool = True,
) -> ScopeResult:
    """Compute the in-scope technique set as an intersection of three filters.

    Filter 1  environment  — techniques your platforms can experience
    Filter 2  threat profile — techniques your prioritised actors actually use
    Filter 3  attack trees  — techniques on a modelled path to a crown jewel

    Tier A  in all three (choke points)
    Tier B  environment + tree (on a path, no public attribution to your actor set)
    Tier C  environment + actor (your adversaries use it, not yet modelled on a path)
    """
    techs = _load_techniques()
    plats = platforms_for(env)
    actors = _load_actors()

    env_ok = {
        r["technique_id"]
        for r in techs
        if not r["platforms"].strip() or (set(p.strip() for p in r["platforms"].split(";")) & plats)
    }
    actor_techs: set[str] = set()
    unknown = []
    for aid in actor_ids:
        a = actors.get(aid)
        if a is None:
            unknown.append(aid)
            continue
        actor_techs |= set(a["techniques"])
    tree_techs = set(tree_techniques)

    in_scope: dict[str, str] = {}
    for t in env_ok:
        on_tree, by_actor = t in tree_techs, t in actor_techs
        if on_tree and by_actor:
            in_scope[t] = "A"
        elif on_tree and include_unattributed_on_path:
            in_scope[t] = "B"
        elif by_actor:
            in_scope[t] = "C"

    counts = {"A": 0, "B": 0, "C": 0}
    for tier in in_scope.values():
        counts[tier] += 1

    notices: list[str] = []
    if unknown:
        notices.append(f"Unknown ATT&CK actor identifiers ignored: {', '.join(unknown)}.")
    if not tree_techs:
        notices.append(
            "No attack trees supplied, so nothing reached Tier A. Every in-scope technique is "
            "Tier C — relevant to your adversaries but not yet placed on a path to a crown jewel. "
            "That is the Tier 2 to Tier 3 gap in the maturity ladder, and it is the single most "
            "useful thing to fix."
        )
    if not actor_techs:
        notices.append(
            "No threat actors selected. Scope is derived from environment and attack trees only, "
            "which is threat modeling without threat intelligence."
        )
    ratio = len(in_scope) / len(techs) if techs else 0
    if ratio > 0.75:
        notices.append(
            f"Scope challenge: {len(in_scope)} of {len(techs)} techniques are in scope "
            f"({ratio*100:.0f}%). At that breadth this is not scoping, it is the absence of "
            f"scoping, and the resulting coverage score will not mean anything. Narrow the actor "
            f"set to those your threat profile actually ranks, or rely on Tier A and B."
        )
    return ScopeResult(in_scope=in_scope, tier_counts=counts, total_techniques=len(techs), notices=notices)


def summarise(env: Environment, scope: ScopeResult) -> dict[str, Any]:
    """Everything the tool needs to tell a user where they stand and what to fix."""
    det = detectability(env, scope.in_scope)
    tier_a = [t for t, v in scope.in_scope.items() if v == "A"]
    gaps = missing_sources(env, scope.in_scope)[:10]
    return {
        "profile": derive_profile(env),
        "platforms": sorted(platforms_for(env)),
        "scope": {
            "in_scope": scope.count,
            "of_total": scope.total_techniques,
            "tiers": scope.tier_counts,
            "notices": scope.notices,
        },
        "detectability": {
            "assessed": det["assessed"],
            "blind": len(det["blind"]),
            "blind_percent": det["blind_percent"],
            "partial": len(det["partial"]),
            "fully_reachable": len(det["full"]),
            "tier_a_blind": sorted(set(tier_a) & set(det["blind"])),
        },
        "highest_value_telemetry_gaps": [
            {"log_source": s, "unblocks_techniques": n} for s, n in gaps
        ],
    }


# ---------------------------------------------------------------------------
# Telemetry assurance
#
# The model's stated purpose here: tell an organisation whether it holds the
# telemetry required to detect a specific threat, and if not, exactly what to
# enable. Assurance is not a yes/no on possession — a source deployed on 60% of
# the estate gives 60% assurance, and the model says so.
# ---------------------------------------------------------------------------
import yaml as _yaml  # noqa: E402

CATALOGUE_PATH = DATA / "telemetry_catalogue.yaml"
_ASSURANCE_BANDS = [
    (90, "assured", "Required telemetry is present across the estate."),
    (60, "partial", "Telemetry exists but does not cover the whole estate; detection is best-effort."),
    (1, "weak", "Telemetry is present on a minority of the estate. Do not rely on this detection."),
    (0, "blind", "No required telemetry. This threat cannot be detected regardless of rule quality."),
]


def load_catalogue() -> dict[str, Any]:
    return _yaml.safe_load(CATALOGUE_PATH.read_text())["sources"]


def _band(pct: float) -> tuple[str, str]:
    for floor, name, note in _ASSURANCE_BANDS:
        if pct >= floor:
            return name, note
    return "blind", _ASSURANCE_BANDS[-1][2]


def technique_requirements(
    technique_ids: Iterable[str], env: "Environment | None" = None
) -> dict[str, dict[str, Any]]:
    """What each technique's ATT&CK analytics actually require, with channels.

    Pass env to restrict to analytics relevant to the platforms actually run.
    """
    wanted = set(technique_ids)
    raw = analytics_for(env) if env is not None else _load_analytics()
    out: dict[str, dict[str, Any]] = {}
    for a in raw:
        if a["t"] not in wanted:
            continue
        rec = out.setdefault(a["t"], {"analytics": 0, "sources": {}})
        rec["analytics"] += 1
        for s in a["s"]:
            rec["sources"].setdefault(s, 0)
            rec["sources"][s] += 1
    return out


def telemetry_assurance(
    env: Environment,
    technique_ids: Iterable[str],
    collection: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Per-threat telemetry assurance.

    collection maps ATT&CK log source name -> estate coverage percentage. When it is
    omitted, coverage is inferred from the declared environment at 100% for reachable
    sources — optimistic, and flagged as such, because "we have Sysmon" and "Sysmon is
    deployed everywhere and healthy" are different claims.
    """
    prefixes = reachable_sources(env)
    inferred = collection is None
    reqs = technique_requirements(technique_ids, env)

    def coverage_for(source: str) -> float:
        if collection is not None:
            for k, v in collection.items():
                if source.startswith(k) or k.startswith(source):
                    return float(v)
            return 0.0
        return 100.0 if _reaches(source, prefixes) else 0.0

    per: dict[str, Any] = {}
    for tid, rec in reqs.items():
        # a technique's assurance is the best coverage among the sources that would
        # detect it — you need one working route, not all of them
        best = max((coverage_for(s) for s in rec["sources"]), default=0.0)
        band, note = _band(best)
        per[tid] = {
            "assurance_percent": round(best, 1),
            "band": band,
            "note": note,
            "analytics": rec["analytics"],
            "required_sources": sorted(rec["sources"], key=lambda s: -rec["sources"][s]),
            "held_sources": sorted(s for s in rec["sources"] if coverage_for(s) > 0),
            "missing_sources": sorted(s for s in rec["sources"] if coverage_for(s) == 0),
        }
    counts: dict[str, int] = {}
    for v in per.values():
        counts[v["band"]] = counts.get(v["band"], 0) + 1
    total = len(per) or 1
    return {
        "inferred_coverage": inferred,
        "caveat": (
            "Coverage inferred from the declared environment at 100%. Supply measured "
            "per-source estate coverage for a defensible assurance figure."
            if inferred else
            "Assurance computed from supplied per-source estate coverage."
        ),
        "per_technique": per,
        "band_counts": counts,
        "assured_percent": round(100 * counts.get("assured", 0) / total, 1),
        "blind_percent": round(100 * counts.get("blind", 0) / total, 1),
    }


def telemetry_recommendations(
    env: Environment,
    technique_ids: Iterable[str],
    collection: dict[str, float] | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """What to enable, ranked by how many in-scope techniques it unblocks.

    Recommends capabilities and, where a capability cannot be met with what the
    organisation already owns, a tool CLASS and its open-source options. It never
    recommends a named commercial product.
    """
    cat = load_catalogue()
    assurance = telemetry_assurance(env, technique_ids, collection)
    blocked: dict[str, set[str]] = {}
    for tid, rec in assurance["per_technique"].items():
        if rec["band"] in ("assured",):
            continue
        for s in rec["missing_sources"]:
            blocked.setdefault(s, set()).add(tid)

    out = []
    for source, techs in sorted(blocked.items(), key=lambda x: -len(x[1])):
        info = cat.get(source, {})
        out.append({
            "log_source": source,
            "unblocks_techniques": len(techs),
            "example_techniques": sorted(techs)[:6],
            "what": (info.get("what") or "").strip() or "Not yet catalogued; see ATT&CK analytics for this source.",
            "key_channels": info.get("key_channels", ""),
            "how_to_enable": (info.get("how") or "").strip(),
            "tool_class": info.get("tool_class", ""),
            "open_source_option": info.get("open_source", ""),
            "substitutes": info.get("substitutes", []),
            "effort": info.get("effort", "unknown"),
            "volume": info.get("volume", "unknown"),
            "catalogued": source in cat,
        })
        if len(out) >= limit:
            break
    return out


def assurance_report(
    env: Environment,
    scope: "ScopeResult",
    collection: dict[str, float] | None = None,
) -> dict[str, Any]:
    """The visibility answer: can we see this threat, and if not, what do we turn on."""
    a = telemetry_assurance(env, scope.in_scope, collection)
    tier_a = {t for t, v in scope.in_scope.items() if v == "A"}
    tier_a_blind = sorted(t for t in tier_a if a["per_technique"].get(t, {}).get("band") == "blind")
    return {
        "summary": {
            "techniques_assessed": len(a["per_technique"]),
            "assured_percent": a["assured_percent"],
            "blind_percent": a["blind_percent"],
            "bands": a["band_counts"],
            "tier_a_blind": tier_a_blind,
            "caveat": a["caveat"],
        },
        "recommendations": telemetry_recommendations(env, scope.in_scope, collection),
    }
