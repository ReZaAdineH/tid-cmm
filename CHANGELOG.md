# Changelog

Changes to the **model and its datasets**. The assessment tool at
<https://tid-cmm.com/assess> has no version of its own: it implements the model and
stamps the model version on every report and export. Site-level changes are recorded on
<https://tid-cmm.com/changelog/>.

The format follows Keep a Changelog. A change to any level descriptor, weight or
sub-capability is a minor version at minimum, because it moves scores.

## [1.6.0] — 2026-09-06

Model **1.6.0** · documents **v1.6** · aligned to MITRE ATT&CK Enterprise v19.2.
A backward-compatible expansion of what an assessment records and reports.

### Added

- **Expanded crown-jewel scoping.** Structured asset types beside the existing categories.
  Choosing one lifts the tactics an adversary must succeed at to reach that asset, names
  the telemetry families that would see it, and offers the scenario templates that fit it.
- **Per-technique detection and validation evidence.** A register recording, for each
  in-scope technique, whether a detection is deployed and enabled, whether the telemetry
  it requires is healthy, and whether it has been validated locally by a controlled
  adversarial method within a stated window. Evidence is named rather than asserted, and
  a validation outside the window expires.
- **Multi-step scenarios and adversary timelines.** Ordered chains to a crown jewel, with
  detection and validation recorded per step, correlation keys between steps, and the
  Scenario Coverage Score: a scenario counts as covered only when it is detected at two or
  more distinct stages, at least one of them validated locally.
- **Known-threat assurance and unknown or emerging-threat readiness**, read through
  sub-capabilities already answered and reported as a reading rather than a coverage
  percentage.
- **Correlation readiness**: cross-domain correlation and adversary-timeline
  reconstruction — what the capability needs as input and what it produces as evidence.
- **Prevention and protection boundary**: where prevention and protection efficacy is
  assessed inside TID-CMM, and what crosses the line into TIR-CMM.
- **Assurance-at-a-glance reporting**: technique assurance, technique assurance by stage,
  scenario status, unknown-threat readiness and the bottlenecks — with counts and
  denominators, and no percentage without one.
- **Standards and UTIOM views, none of them scoring**: non-scoring views onto NIST CSF 2.0,
  SOC-CMM and ISO/IEC 27001 where a mapping has been reviewed, and the UTIOM operating
  model. No level, mapping, score or percentage is invented in a view.
- **TIR-CMM handoff.** The assessment exports `tid-cmm/export/1.0`, which satisfies the
  TIR-CMM import contract and carries the provenance a score needs to travel.

### Unchanged

- The maturity arithmetic is the arithmetic of 1.5.0: the same eight domains and weights,
  the same 58 sub-capabilities and 348 level descriptors, and the same integrity
  constraints C1–C5 applied in the same order (C3 → C5 → C4 → C2 → C1). For identical
  maturity responses the overall and domain maturity scores are numerically comparable
  with 1.5.0. The technique, scenario and readiness outputs are new, and are comparable
  only where those fields have been assessed.
- An assessment saved under 1.5.0 imports without changing the answers it recorded; the
  saved-assessment format is unchanged.

### Licensing

- Model 1.6.0, documents v1.6 and the current site are free to use under the permitted-use
  terms in `LICENSE` (canonical statement: https://tid-cmm.com/licence/). Free to use does
  not mean open source, public domain, or permission to redistribute, rebrand or create
  derivative products. Model 1.5.0 and documents v1.4 keep the licence they were released
  under.

## [1.5.0] — 2026-08-20

### Changed

- Workload and identity can be more than one thing. Picking a single workload dropped the
  other workloads' techniques from scope; picking a single identity provider hid the
  telemetry of the rest. **Changes scores** wherever more than one applies.
- AWS IAM and Identity Center, Google Workspace and Ping added as identity providers.
- Regulated organisations are never placed on the essential profile, and the named regime
  is recorded on the report. The tool shows why a profile was derived, not only what.
- The model, the documents and the site are versioned separately; the assessment tool
  stamps the model version onto the report and the export.

## [1.3.0] — 2026-08-17

### Added

- Suggested threat profile: declare sector and regions, and the tool ranks the adversaries
  ATT&CK documents against organisations like yours.
- A dataset covering all 232 documented groups and campaigns.
- **C5, the inherited intent ceiling.** Changes scores where the suggested profile is
  accepted without review. Five constraints from this version on.

## [1.2.1] — 2026-08-17

- Licensing stated as three things at the time: the model and the data under CC BY 4.0,
  and the assessment tool free to use but not to redistribute. (Corrected 2026-09-05: the
  entry originally also named a "reference engine under Apache-2.0"; no such engine is
  published, and the claim is withdrawn.) The current terms are in `LICENSE`.
- The 2022 origin on the record; TIR-CMM published at https://tir-cmm.com.

## [1.2.0] — 2026-08-15

### Changed

- **AA.7 Deception and adversary engagement** — level 4 now also expects breadcrumbs that
  lead credibly toward the decoys rather than leaving them to be stumbled upon, and a
  measured alert-noise rate. Evidence gains a measured noise rate including periods with
  no trips. Placement research is consistent that a decoy an adversary never encounters
  is worth less than a simple one they do.

### Unchanged

- 8 domains, 58 sub-capabilities, 348 level descriptors. Domain weights, sub-capability
  weights and the four integrity constraints are unchanged, so **scores from 1.1.0 remain
  directly comparable**.

## [1.1.0] — 2026-08-12

### Added

- Fourth integrity constraint **C4 — intent ceiling**: DC and DE may not exceed
  max(TI, TM) + 1. Sensors and content without architectural intent produce noise.
- Maturity tiers with entry gates, so a high weighted score alone does not buy a tier.
- Applicability profiles — essential, standard, comprehensive — so a small organisation is
  not assessed against the burden of a large regulated one.
- Detection classes: decisive, corroborative, and hunting or context.

### Changed

- Expanded from 53 to 58 sub-capabilities, and from three constraints to four.
- ATT&CK alignment moved to Enterprise v19.2, which restructured detection into strategies
  and analytics referencing concrete log sources.

## [1.0.0] — 2026-08-10

- First public version: 8 domains, 53 sub-capabilities, three integrity constraints.
