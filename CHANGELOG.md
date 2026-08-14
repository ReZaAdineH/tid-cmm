# Changelog

All notable changes to TID-CMM are recorded here. The format follows Keep a Changelog; the project uses semantic versioning as described in CONTRIBUTING.md.

## [1.0.0] — 2026-08-10

First complete release. The model moves from a six-domain outline to a full, assessable framework with working tooling.

### Added

- **Eight domains, 53 sub-capabilities, 318 level descriptors.** Every sub-capability has an assessment question, complete 0–5 descriptors, evidence criteria and framework crosswalks.
- **Two new domains** beyond the original outline:
  - `TM` — Threat Modeling & Attack Path Analysis (attack trees, computed attack paths, abuse-case traceability, model maintenance triggers).
  - `AV` — Adversarial Validation & Emulation (atomic testing, BAS, threat-actor emulation, purple team, penetration testing integration, red teaming, findings-to-closure, control efficacy scoring).
- **Three integrity constraints** (C1 validation ceiling, C2 visibility ceiling, C3 evidence rule), applied mechanically by the scoring engine and reported explicitly.
- **ATT&CK Validated Coverage Score** — a four-point per-technique scale separating telemetry, detection logic and emulation-proven detection, computed over an honestly scoped in-scope set.
- **Python package** `tidcmm` with model loader, validator, scoring engine and CLI.
- **Excel self-assessment workbook** — 11 tabs, live formulas, radar chart, full ATT&CK technique list, ranked roadmap, crosswalk.
- **Single-file browser assessment tool** — no server, no CDN, no network traffic, JSON and CSV import/export, printable report.
- **59-page white paper** in DOCX and PDF, with the full sub-capability register and crosswalk as appendices.
- **Alignment to MITRE ATT&CK Enterprise v19.2** (697 techniques: 222 parent, 475 sub; 109 data components; 15 tactics), snapshot 2026-08-05.
- **Crosswalks** to NIST CSF 2.0, SOC-CMM, ISO/IEC 27001:2022, MITRE D3FEND, Gartner CTEM and Elastic DEBMM at sub-capability level.
- **Test suite** (18 tests) asserting model integrity, scoring maths, constraint behaviour, coverage boundaries and agreement between the three independent implementations.

### Changed from the original outline

- The original six domains are retained in substance and renamed for precision:
  - *Threat Detection Coverage* → `DC` Telemetry & Detection Coverage, with telemetry quality and normalisation added as distinct sub-capabilities.
  - *Threat Intelligence Integration* → `TI` Threat Intelligence & Adversary Prioritisation, with prioritisation and intel-to-detection tasking made explicit.
  - *Analytics & Automation* → `AA` Analytics, Automation & Hunting, with threat hunting brought in as a producer of detection.
- Scoring is now weighted rather than a flat mean, with weights exposed as editable parameters.

### Known limitations

- Weights are a judgement and are not empirically derived. They are exposed for challenge.
- Crosswalk mappings are indicative and one-to-many; they are not a claim of equivalence.
- There is no benchmark dataset yet. Sector comparison requires contributed anonymised assessments.
