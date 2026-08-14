"""Tests for the TID-CMM model definition and scoring engine."""
import csv
from pathlib import Path

import pytest

from tidcmm.model import load_model, validate_model
from tidcmm.scoring import Response, band_for, compute_coverage, score_assessment

ROOT = Path(__file__).resolve().parent.parent
MODEL = load_model()


# --------------------------------------------------------------------------
# Model integrity
# --------------------------------------------------------------------------
def test_model_validates_clean():
    assert validate_model(MODEL) == []


def test_domain_weights_sum_to_100():
    assert sum(d.weight for d in MODEL.domains) == pytest.approx(100)


def test_subcapability_weights_sum_to_100_per_domain():
    for d in MODEL.domains:
        assert sum(s.weight for s in d.subcapabilities) == pytest.approx(100), d.id


def test_every_subcapability_has_six_level_descriptors():
    for s in MODEL.subcapabilities():
        assert sorted(s.levels) == [0, 1, 2, 3, 4, 5], s.id


def test_expected_shape():
    assert len(MODEL.domains) == 8
    # the register grows; assert the invariants, not a frozen count
    assert len(MODEL.subcapabilities()) >= 53
    assert len(MODEL.subcapabilities()) == len({s.id for s in MODEL.subcapabilities()})


def test_every_subcapability_has_a_valid_profile():
    valid = {"essential", "standard", "comprehensive"}
    for s in MODEL.subcapabilities():
        assert s.profile in valid, f"{s.id} has profile {s.profile!r}"


def test_profiles_are_nested_and_essential_is_proportionate():
    counts = {}
    for s in MODEL.subcapabilities():
        counts[s.profile] = counts.get(s.profile, 0) + 1
    # Essential must stay small enough for a team with no detection engineer
    assert counts["essential"] <= 25, counts
    assert counts["essential"] >= 15, counts
    assert sum(counts.values()) == len(MODEL.subcapabilities())


def test_essential_profile_spans_every_domain():
    """A profile that skips a domain would tell a small organisation that whole
    parts of detection do not apply to them."""
    for d in MODEL.domains:
        assert any(s.profile == "essential" for s in d.subcapabilities), d.id


def test_four_integrity_constraints_present():
    ids = [c["id"] for c in MODEL.meta["scoring"]["constraints"]]
    assert ids == ["C1", "C2", "C3", "C4"]


def test_detection_classes_and_archetypes_defined():
    classes = MODEL.meta["detection_classes"]["classes"]
    assert [c["id"] for c in classes] == ["D", "C", "H"]
    assert MODEL.meta["profiles"]["derivation"]["rationale_required"] is True
    assert len(MODEL.meta["environment_archetypes"]["dimensions"]) >= 6


def test_every_subcapability_has_nist_csf_crosswalk():
    for s in MODEL.subcapabilities():
        assert s.crosswalk.get("nist_csf_2"), s.id


def test_attack_alignment_matches_bundled_dataset():
    with open(ROOT / "data" / "attack_techniques.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    align = MODEL.meta["alignment"]["attack"]
    assert len(rows) == align["techniques"]
    assert sum(1 for r in rows if r["is_subtechnique"] == "No") == align["parent_techniques"]
    assert sum(1 for r in rows if r["is_subtechnique"] == "Yes") == align["sub_techniques"]


# --------------------------------------------------------------------------
# Scoring maths
# --------------------------------------------------------------------------
def _uniform(score, evidence="ev"):
    return {
        s.id: Response(s.id, score, evidence=evidence)
        for s in MODEL.subcapabilities()
    }


def test_uniform_scores_roll_up_exactly():
    for n in range(6):
        r = score_assessment(MODEL, _uniform(n))
        assert r.overall_score == pytest.approx(n)
        for d in r.domains:
            assert d.adjusted_score == pytest.approx(n)


def test_bands():
    assert band_for(0.0).startswith("Level 0")
    assert band_for(2.99).startswith("Level 2")
    assert band_for(3.0).startswith("Level 3")
    assert band_for(5.0).startswith("Level 5")


def test_c3_downgrades_unevidenced_high_scores():
    r = score_assessment(MODEL, _uniform(5, evidence=""))
    assert r.overall_score == pytest.approx(3)
    assert all("C3" in line for line in r.constraint_log)


def test_c3_not_applied_in_non_strict_mode():
    r = score_assessment(MODEL, _uniform(5, evidence=""), strict=False)
    assert r.overall_score == pytest.approx(5)
    assert r.constraint_log == []


def test_c1_validation_ceiling():
    resp = _uniform(5)
    for s in MODEL.domain("AV").subcapabilities:
        resp[s.id] = Response(s.id, 1, evidence="ev")
    r = score_assessment(MODEL, resp)
    av = next(d for d in r.domains if d.id == "AV")
    assert av.adjusted_score == pytest.approx(1)
    for d in r.domains:
        assert d.adjusted_score <= av.adjusted_score + 1 + 1e-9, d.id


def test_c2_visibility_ceiling():
    resp = _uniform(3)
    for s in MODEL.domain("DE").subcapabilities:
        resp[s.id] = Response(s.id, 5, evidence="ev")
    r = score_assessment(MODEL, resp)
    dc = next(d for d in r.domains if d.id == "DC")
    de = next(d for d in r.domains if d.id == "DE")
    assert de.adjusted_score <= dc.adjusted_score + 1 + 1e-9
    assert any("C2" in line for line in r.constraint_log)


def test_not_applicable_excluded_from_rollup():
    resp = _uniform(4)
    gv = MODEL.domain("GV")
    resp[gv.subcapabilities[-1].id] = Response(gv.subcapabilities[-1].id, None)
    r = score_assessment(MODEL, resp)
    got = next(d for d in r.domains if d.id == "GV")
    assert got.not_applicable == 1
    assert got.adjusted_score == pytest.approx(4)


def test_priorities_are_ranked_by_weighted_impact():
    resp = _uniform(1)
    r = score_assessment(MODEL, resp)
    impacts = [p["impact"] for p in r.priorities]
    assert impacts == sorted(impacts, reverse=True)
    assert all(p["gap"] > 0 for p in r.priorities)


# --------------------------------------------------------------------------
# Coverage score
# --------------------------------------------------------------------------
def test_coverage_score_boundaries():
    rows = [{"technique_id": f"T{i:04d}", "tactics": "Execution", "in_scope": True, "status": 3} for i in range(10)]
    assert compute_coverage(rows)["vcs_percent"] == 100.0
    for r in rows:
        r["status"] = 0
    assert compute_coverage(rows)["vcs_percent"] == 0.0
    for i, r in enumerate(rows):
        r["status"] = 2 if i < 5 else 1
    c = compute_coverage(rows)
    assert c["vcs_percent"] == pytest.approx(50.0)
    assert c["detected_or_better_percent"] == pytest.approx(50.0)
    assert c["validated_percent"] == pytest.approx(0.0)


def test_coverage_ignores_out_of_scope():
    rows = [
        {"technique_id": "T1001", "tactics": "Impact", "in_scope": True, "status": 3},
        {"technique_id": "T1002", "tactics": "Impact", "in_scope": False, "status": 0},
    ]
    c = compute_coverage(rows)
    assert c["in_scope"] == 1
    assert c["vcs_percent"] == 100.0


# --------------------------------------------------------------------------
# Worked example
# --------------------------------------------------------------------------
def test_example_assessment_scores_and_constraints_bite():
    import yaml

    data = yaml.safe_load((ROOT / "assessments" / "example-assessment.yaml").read_text())
    resp = {
        k: Response(k, v.get("score"), evidence=v.get("evidence", "") or "",
                    target=v.get("target"), owner=v.get("owner", "") or "")
        for k, v in data["responses"].items()
    }
    r = score_assessment(MODEL, resp, organisation=data["organisation"])
    assert 0 <= r.overall_score <= 5
    assert r.overall_score < r.overall_raw, "constraints should reduce the self-assessed score"
    assert any(line.startswith("C1") for line in r.constraint_log)


# --------------------------------------------------------------------------
# JSON Schema
# --------------------------------------------------------------------------
def test_model_matches_published_json_schema():
    jsonschema = pytest.importorskip("jsonschema")
    import json

    schema = json.loads((ROOT / "model" / "schema" / "model.schema.json").read_text())
    doc = MODEL.to_dict()
    doc["domains"] = [
        {**d, "subcapabilities": [
            {**s, "levels": {str(k): v for k, v in s["levels"].items()}}
            for s in d["subcapabilities"]
        ]}
        for d in doc["domains"]
    ]
    jsonschema.validate(doc, schema)


def test_example_assessment_matches_assessment_schema():
    jsonschema = pytest.importorskip("jsonschema")
    import json

    import yaml

    schema = json.loads((ROOT / "model" / "schema" / "assessment.schema.json").read_text())
    data = yaml.safe_load((ROOT / "assessments" / "example-assessment.yaml").read_text())
    data["assessed_on"] = str(data["assessed_on"])
    jsonschema.validate(data, schema)


def test_every_response_id_exists_in_the_model():
    import yaml

    data = yaml.safe_load((ROOT / "assessments" / "example-assessment.yaml").read_text())
    known = {s.id for s in MODEL.subcapabilities()}
    assert set(data["responses"]) == known


# --------------------------------------------------------------------------
# Scoping and detectability
# --------------------------------------------------------------------------
from tidcmm.scoping import (  # noqa: E402
    Environment, challenge_profile, derive_profile, derive_scope,
    detectability, missing_sources, platforms_for, summarise,
)

SMALL = Environment(operating_model="no-soc", size="small")
BANK = Environment(estate="hybrid", cloud="azure", productivity="microsoft-365",
                   identity="entra-id", endpoint_telemetry="commercial-edr",
                   network_telemetry="inline-inspection", workload="containers",
                   operating_model="in-house-soc", regulated=True, size="large")


def test_profile_derivation_is_proportionate():
    assert derive_profile(SMALL) == "essential"
    assert derive_profile(BANK) == "comprehensive"


def test_profile_challenge_fires_only_when_narrowing():
    assert challenge_profile(BANK, "essential") is not None
    assert challenge_profile(BANK, "comprehensive") is None
    assert challenge_profile(SMALL, "comprehensive") is None


def test_scope_is_an_intersection_not_the_whole_matrix():
    s = derive_scope(SMALL, actor_ids=["G0102"], tree_techniques=["T1486"])
    assert 0 < s.count < s.total_techniques
    assert s.tier_counts["A"] >= 1  # on a tree and used by the actor


def test_scope_without_trees_yields_no_tier_a_and_says_so():
    s = derive_scope(SMALL, actor_ids=["G0102"], tree_techniques=[])
    assert s.tier_counts["A"] == 0
    assert any("Tier A" in n for n in s.notices)


def test_over_broad_scope_is_challenged():
    every_actor = [r.split(",")[0] for r in
                   (ROOT / "data" / "attack_actors.csv").read_text().splitlines()[1:]]
    s = derive_scope(BANK, actor_ids=every_actor, tree_techniques=[])
    assert any("Scope challenge" in n for n in s.notices)


def test_telemetry_changes_what_is_detectable():
    """The core claim: instrumentation choice moves the blind set, and the model
    can say by how much without naming a product."""
    blind_bare = detectability(Environment(endpoint_telemetry="none"))["blind_percent"]
    blind_native = detectability(Environment(endpoint_telemetry="native-os-logging-only"))["blind_percent"]
    blind_oss = detectability(Environment(endpoint_telemetry="open-source-instrumentation"))["blind_percent"]
    assert blind_bare > blind_native > blind_oss


def test_open_source_instrumentation_is_a_viable_path():
    """An organisation with no commercial tooling must not be structurally
    excluded from high maturity."""
    oss = detectability(Environment(endpoint_telemetry="open-source-instrumentation"))
    edr = detectability(Environment(endpoint_telemetry="commercial-edr"))
    assert oss["blind_percent"] - edr["blind_percent"] < 10


def test_missing_sources_are_ranked_by_techniques_unblocked():
    s = derive_scope(SMALL, actor_ids=["G0102"], tree_techniques=["T1486"])
    gaps = missing_sources(SMALL, s.in_scope)
    assert gaps
    assert [g[1] for g in gaps] == sorted((g[1] for g in gaps), reverse=True)


def test_advisory_passes_through_attack_vocabulary_without_adding_recommendations():
    """ATT&CK's log source names sometimes include a vendor channel (m365:defender).
    That is MITRE's vocabulary, passed through verbatim. What must never happen is
    TID-CMM introducing a product name of its own — so the assertion belongs on the
    model's descriptors, not on ATT&CK's data."""
    import csv as _csv
    with open(ROOT / "data" / "attack_log_sources.csv", newline="") as f:
        vocabulary = {r["log_source"] for r in _csv.DictReader(f)}
    gaps = missing_sources(SMALL, derive_scope(SMALL, actor_ids=["G0102"]).in_scope)
    assert all(g[0] in vocabulary for g in gaps), "advisory invented a source name"

    # Naming a public report or open rule repository as an example is legitimate.
    # Requiring a product to reach a level is not. Any sub-capability that mentions a
    # commercial name must present it as an example and must carry a note saying no
    # level depends on it.
    commercial = ("crowdstrike", "mandiant", "red canary", "splunk", "elastic",
                  "sentinelone", "carbon black", "qradar", "arcsight", "cortex xdr")
    for sub in MODEL.subcapabilities():
        blob = " ".join(sub.levels.values()).lower()
        hits = [c for c in commercial if c in blob]
        if not hits:
            continue
        assert "for example" in blob or "such as" in blob, (
            f"{sub.id} names {hits} without presenting them as examples")


def test_summary_is_complete_enough_to_drive_the_tool():
    s = derive_scope(BANK, actor_ids=["G0016"], tree_techniques=["T1486"])
    out = summarise(BANK, s)
    for key in ("profile", "platforms", "scope", "detectability", "highest_value_telemetry_gaps"):
        assert key in out
    assert out["scope"]["tiers"]["A"] + out["scope"]["tiers"]["B"] + out["scope"]["tiers"]["C"] == s.count


# --------------------------------------------------------------------------
# Telemetry assurance — "do I have the visibility to detect this threat?"
# --------------------------------------------------------------------------
from tidcmm.scoping import (  # noqa: E402
    assurance_report, load_catalogue, technique_requirements,
    telemetry_assurance, telemetry_recommendations,
)

RANSOM_CHAIN = ["T1566.001", "T1204.002", "T1059.001", "T1547.001",
                "T1003.001", "T1021.001", "T1486", "T1490"]


def test_every_technique_has_stated_telemetry_requirements():
    reqs = technique_requirements(RANSOM_CHAIN)
    assert set(reqs) == set(RANSOM_CHAIN)
    for tid, r in reqs.items():
        assert r["analytics"] > 0 and r["sources"], tid


def test_assurance_distinguishes_inferred_from_measured():
    inferred = telemetry_assurance(SMALL, RANSOM_CHAIN)
    measured = telemetry_assurance(SMALL, RANSOM_CHAIN, {"WinEventLog:Security": 90})
    assert inferred["inferred_coverage"] is True
    assert measured["inferred_coverage"] is False
    assert "measured" in measured["caveat"] or "supplied" in measured["caveat"]


def test_estate_coverage_drives_the_assurance_band():
    """Possession is not assurance. A source on 30% of the estate must not read as
    the same capability as one deployed everywhere."""
    full = telemetry_assurance(SMALL, RANSOM_CHAIN, {"WinEventLog:Security": 100})
    thin = telemetry_assurance(SMALL, RANSOM_CHAIN, {"WinEventLog:Security": 30})
    none = telemetry_assurance(SMALL, RANSOM_CHAIN, {})
    assert full["assured_percent"] > thin["assured_percent"]
    assert none["blind_percent"] == 100.0
    bands = {v["band"] for v in thin["per_technique"].values()}
    assert bands <= {"weak", "partial", "blind"}


def test_blind_techniques_produce_actionable_recommendations():
    recs = telemetry_recommendations(Environment(endpoint_telemetry="none"), RANSOM_CHAIN)
    assert recs
    top = recs[0]
    assert top["unblocks_techniques"] >= 1
    assert top["catalogued"], "highest-value gap should carry enable guidance"
    assert top["how_to_enable"] and top["tool_class"]


def test_recommendations_are_ranked_by_value():
    recs = telemetry_recommendations(Environment(endpoint_telemetry="none"), RANSOM_CHAIN)
    counts = [r["unblocks_techniques"] for r in recs]
    assert counts == sorted(counts, reverse=True)


def test_guidance_names_tool_classes_and_free_options_not_products():
    cat = load_catalogue()
    banned = ("crowdstrike", "splunk", "sentinelone", "carbon black", "qradar",
              "arcsight", "cortex", "darktrace", "rapid7")
    for name, info in cat.items():
        blob = " ".join(str(v) for v in info.values()).lower()
        assert not any(b in blob for b in banned), f"{name} names a commercial product"
        assert info.get("tool_class"), f"{name} has no tool class"


def test_catalogue_covers_the_highest_value_sources():
    """The guidance must cover the sources that actually block the most detection."""
    cat = load_catalogue()
    for critical in ("WinEventLog:Sysmon", "WinEventLog:Security", "auditd:SYSCALL",
                     "AWS:CloudTrail", "m365:unified", "azure:signinlogs", "NSM:Flow"):
        assert critical in cat, critical


def test_assurance_report_names_the_tier_a_blind_spots():
    """The headline the model exists to produce: the choke points you cannot see."""
    env = Environment(endpoint_telemetry="native-os-logging-only")
    scope = derive_scope(env, actor_ids=["G0102"], tree_techniques=RANSOM_CHAIN)
    rep = assurance_report(env, scope, {"WinEventLog:Security": 92})
    s = rep["summary"]
    assert s["techniques_assessed"] > 0
    assert 0 <= s["assured_percent"] <= 100
    assert isinstance(s["tier_a_blind"], list)
    assert rep["recommendations"]
