# TID-CMM — Threat-Informed Detection Capability Maturity Model

**A framework for measuring whether your detection capability is driven by adversary behaviour — and whether it has been proven to work.**

[![Model](https://img.shields.io/badge/model-v1.1.0-d2661c)](model/meta.yaml)
[![CI](https://github.com/ReZaAdineH/tid-cmm/actions/workflows/ci.yml/badge.svg)](https://github.com/ReZaAdineH/tid-cmm/actions/workflows/ci.yml)
[![ATT&CK](https://img.shields.io/badge/ATT%26CK-Enterprise%20v19.2-0b2545)](https://attack.mitre.org/)
[![Licence](https://img.shields.io/badge/model-CC--BY--4.0-green)](LICENSE)
[![Code](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE-CODE)

Most organisations cannot answer a simple question about their own security operations: *against the adversaries most likely to attack us, what proportion of their behaviour would we actually see — and how do we know?*

TID-CMM exists to answer it. **8 domains · 58 sub-capabilities · 348 level descriptors · aligned to MITRE ATT&CK Enterprise v19.2 (697 techniques).**

---

> **423 techniques — 89% of all Windows techniques in ATT&CK Enterprise v19.2 — have detection
> analytics that reference Sysmon.** For 20 of them it is the only source referenced. If you do
> not run Sysmon or an EDR supplying equivalent process, command line and module telemetry,
> that is not a gap in your rule set. It is a gap in physics.
>
> TID-CMM computes that for *your* scoped technique set, and tells you what to enable.

---

## What makes this different

Three things, and they are the whole point.

**1. Adversarial validation is a first-class domain.** Atomic testing, breach and attack simulation, threat-actor emulation, purple teaming, penetration testing and red teaming are scored together as the evidence engine of the model — not as a footnote under "testing".

**2. Threat modeling and attack path analysis is a first-class domain.** Threat intelligence tells you what an adversary does in general. Attack trees and computed attack paths tell you what that behaviour looks like against *your* architecture, identities and crown jewels. Without that step, ATT&CK coverage is a generic checklist.

**3. The model refuses to let an assessment flatter itself.** Four integrity constraints are applied mechanically at scoring time:

| | Constraint | Rule |
|---|---|---|
| **C1** | Validation ceiling | No domain may exceed the AV domain score + 1. *An untested capability is an assumed capability.* |
| **C2** | Visibility ceiling | DE may not exceed DC + 1. *Detection logic cannot outrun its telemetry.* |
| **C3** | Evidence rule | A score of 4 or 5 without a named artefact is counted as 3. |
| **C4** | Intent ceiling | DC and DE may not exceed max(TI, TM) + 1. *Sensors without architectural intent produce noise, not defence.* |

In the worked example, an organisation with genuinely strong operations self-assesses at **2.44** and scores **2.34** after constraints — because four separate domains were capped by a validation score of 1.63. The model does not just report a lower number; it identifies the one investment that would raise every other domain.

---

## The eight domains

| ID | Domain | Weight | Sub-caps | Question it answers |
|---|---|---|---|---|
| **TI** | Threat Intelligence & Adversary Prioritisation | 12% | 6 | Who are we defending against, and how do we know? |
| **TM** | Threat Modeling & Attack Path Analysis | 12% | 7 | What do their behaviours look like against our architecture? |
| **DC** | Telemetry & Detection Coverage | 14% | 6 | Can we see the activity at all? |
| **DE** | Detection Engineering | 16% | 10 | Do we build, test and maintain detection like engineers? |
| **AV** | Adversarial Validation & Emulation | 14% | 8 | Have we proven any of it works? |
| **AA** | Analytics, Automation & Hunting | 12% | 8 | Does detection output become a decision at operational tempo? |
| **IR** | Incident Response & Recovery | 10% | 6 | Can we act on what we detect? |
| **GV** | Governance, Metrics & Continuous Improvement | 10% | 7 | Is this directed, measured and sustainable? |

## The maturity scale

| Level | Name | Meaning |
|---|---|---|
| 0 | Absent | The capability does not exist in any recognisable form. |
| 1 | Ad hoc | Happens by individual initiative. Undocumented, lost when the individual leaves. |
| 2 | Repeatable | Documented and consistent, but driven by compliance or vendor defaults rather than adversary behaviour. |
| 3 | Threat-Informed | Driven by a prioritised adversary profile, ATT&CK-mapped, traceable to a threat driver. |
| 4 | Measured & Validated | Quantitatively managed and proven by emulation. |
| 5 | Adaptive | A self-correcting closed loop that contributes back to the community. |

---

## Quick start

### I want to run an assessment right now, with no installation

Run it online at **[tid-cmm.com/assess](https://tid-cmm.com/assess)**, or download the [offline single-file version](https://github.com/ReZaAdineH/tid-cmm/releases/latest/download/tid-cmm-assessment.html). A single self-contained file — no server, no CDN, no network traffic. Click **Load worked example** to see a completed assessment.

- **Dark mode**, following your system preference and remembered between visits
- **Back / Next through all 13 pages**, with per-domain completion badges and a progress bar (`Alt+←` / `Alt+→`)
- **Autosave** to your own browser, so a half-finished assessment survives a closed tab
- **Action plan** — a generated 30/60/90-day plan: what to do, in what order, who owns it, and the artefact that proves it is done
- **Export** to JSON and CSV, or print to PDF

### I want to publish it at tid-cmm.com

```bash
python tools/build_site.py     # or: make site
```

Produces `build/tid-cmm-site-upload.zip` — drag it into Cloudflare Pages (Workers & Pages → Create → Pages → Upload assets). Landing page, the tool at `/assess`, the guide and scoring reference as HTML, a downloads index, a CORS-enabled JSON API, security headers, a sitemap, and `_redirects` mapping the existing WordPress URLs so old links keep working. `wrangler.jsonc` is included if you would rather deploy with Workers. See `build/site/DEPLOY.md`.

### I want to run it in a workshop, offline, in Excel

Download the **[self-assessment workbook](https://github.com/ReZaAdineH/tid-cmm/releases/latest/download/TID-CMM-Self-Assessment-v1.1.xlsx)**. Fifteen tabs: read-me, setup, eight domain tabs with the full 0–5 descriptors as cell comments, all 697 ATT&CK techniques, a dashboard with radar and gap charts, a ranked roadmap, a framework crosswalk and the complete descriptor reference.

### I want to score it in a pipeline

```bash
pip install -r requirements.txt

python -m tidcmm validate                      # check the model is internally consistent
python -m tidcmm template my-assessment.yaml   # generate a blank assessment
$EDITOR my-assessment.yaml
python -m tidcmm score my-assessment.yaml -o report.json \
       --coverage my-coverage.csv
```

Example output:

```
========================================================================
TID-CMM assessment — Northgate Financial Services  (2026-08-10)
========================================================================
  TI  Threat Intelligence & Adversary Prioritisation  ██████████·········· 2.62
  TM  Threat Modeling & Attack Path Analysis          ██████·············· 1.48
  DC  Telemetry & Detection Coverage                  ███████████········· 2.63 *
  DE  Detection Engineering                           ███████████········· 2.63 *
  AV  Adversarial Validation & Emulation              ███████············· 1.63
  AA  Analytics, Automation & Hunting                 ███████████········· 2.63 *
  IR  Incident Response & Recovery                    ███████████········· 2.63 *
  GV  Governance, Metrics & Continuous Improvement    ██████████·········· 2.57
------------------------------------------------------------------------
  OVERALL: 2.34  (Level 2 — Repeatable)
  Unadjusted self-assessed score was 2.44.
  ATT&CK Validated Coverage Score: 47.4%  (581 techniques in scope, 12.7% validated)

  Integrity constraints applied:
    - C1: DC 2.84 exceeds AV 1.63 + 1; capped to 2.63.
    - C1: DE 2.74 exceeds AV 1.63 + 1; capped to 2.63.
    - C1: AA 2.81 exceeds AV 1.63 + 1; capped to 2.63.
    - C1: IR 2.86 exceeds AV 1.63 + 1; capped to 2.63.
```

### I want to read the theory

**[White paper (PDF, 60 pages)](https://github.com/ReZaAdineH/tid-cmm/releases/latest/download/TID-CMM-White-Paper-v1.1.pdf)** — 60 pages covering the rationale, positioning against SOC-CMM / DEBMM / CTEM / NIST CSF 2.0, the full model, the assessment method, the scoring mechanics and a complete worked example, with the full sub-capability register and crosswalk as appendices.

---

## The Validated Coverage Score

TID-CMM replaces "% of ATT&CK covered" with a metric that is harder to game. Each **in-scope** technique is scored:

| Status | Meaning |
|---|---|
| 0 | No telemetry — you are blind |
| 1 | Telemetry only — queryable, nothing alerts |
| 2 | Detection logic exists — deployed and healthy, but unproven |
| 3 | Validated by emulation — proven to fire, within the recency window |

`VCS = achieved points / (3 × in-scope techniques)`

Two rules make it meaningful:

- **In-scope means in-scope.** Techniques you cannot experience (no macOS estate, no containers) are excluded, with the rationale recorded. Reporting against the full 697 is a vanity metric.
- **Status 3 expires.** A validation result older than your review window drops to 2. A detection proven eighteen months ago, across two platform migrations, is not proven now.

In the worked example this is the difference between reporting **48.9% coverage** (the industry-standard figure, which would pass unchallenged in most board packs) and **12.7% actually proven**.

---

## Repository layout

```
model/                     The model itself — machine-readable, the source of truth
  meta.yaml                Levels, weights, scoring rules, integrity constraints
  domains/*.yaml           One file per domain: sub-capabilities, 0–5 descriptors,
                           evidence criteria, NIST CSF 2.0 / SOC-CMM crosswalks
  schema/                  JSON Schema for the model and for assessment files

tidcmm/                    Python package
  model.py                 Loader and validator
  scoring.py               Scoring engine: C1/C2/C3, rollups, VCS, prioritisation
  cli.py                   validate · export-json · template · score

tools/                     Build scripts (regenerate everything in build/)
  build_workbook.py        The Excel workbook
  build_app.py             The single-file browser tool
  build_whitepaper.js      The white paper
  fill_example.py          Populates the worked-example workbook

data/
  attack_techniques.csv    Normalised ATT&CK Enterprise v19.2: tactics, platforms,
                           required data components, detection guidance, mitigations

assessments/
  blank-assessment.yaml    Template
  example-assessment.yaml  Fully worked example

docs/                      Assessment guide, scoring reference, contribution guide
tests/                     18 tests covering model integrity and scoring maths
build/                     Generated deliverables (checked in for convenience)
  site/                    The deployable Cloudflare site
  tid-cmm-site.zip         Drag this into Cloudflare Pages
```

## Rebuilding everything

```bash
make all        # validate, test, and regenerate every deliverable
make validate   # model integrity only
make test       # test suite
```

or without make:

```bash
python -m tidcmm validate
python -m pytest tests -q
python -m tidcmm export-json build/model.json
python tools/build_workbook.py build/TID-CMM-Self-Assessment-v1.1.xlsx
python tools/fill_example.py
python tools/build_app.py build/tid-cmm-assessment.html
node tools/build_whitepaper.js build/TID-CMM-White-Paper-v1.1.docx
python tools/build_site.py
```

The Python engine, the Excel workbook and the browser tool implement the same arithmetic independently. `tests/` asserts they agree to two decimal places on the worked example, including the constraint log — because all three will be used by different people in the same organisation, and a discrepancy would undermine the assessment more effectively than any methodological criticism.

---

## How this relates to what you already run

TID-CMM is designed to sit alongside, not replace, the frameworks you have.

| Framework | Relationship |
|---|---|
| **MITRE ATT&CK** | Consumed. Every coverage claim is anchored to technique and sub-technique IDs at v19.2. |
| **SOC-CMM** | Complementary. SOC-CMM assesses the SOC as an operating unit; TID-CMM asks whether it would see the adversary. Crosswalked per sub-capability. |
| **NIST CSF 2.0** | Reporting layer. Every sub-capability maps to CSF outcomes so a TID-CMM assessment feeds existing reporting without a second exercise. |
| **Elastic DEBMM** | Overlapping in the DE domain, and compatible. DEBMM goes deeper on detection engineering behaviour; TID-CMM covers the whole loop. |
| **Gartner CTEM** | Complementary. CTEM asks whether an exposure can be exploited; TID-CMM asks whether the exploitation would be seen. TM.4 is explicitly crosswalked. |
| **ISO/IEC 27001:2022** | Control-existence oriented; TID-CMM is the evidence layer underneath. |

See Appendix B of the white paper, or the `Crosswalk` tab of the workbook, for the full sub-capability-level mapping.

---

## Contributing

The model is open and versioned. Level descriptors, weights, crosswalks and the scoping guidance are all open to challenge by pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

Particularly wanted:

- **Descriptor challenges.** If a level descriptor does not match what you see in practice, say so with the counter-example.
- **Crosswalks.** DORA, NIS2, PCI DSS 4.0, CMMC, sector-specific frameworks.
- **Anonymised assessment data**, for sector benchmarking.
- **Weight arguments.** The weights are a judgement. Argue for a better one with reasoning.

## Licence and status

Model content is **CC-BY-4.0**. Code and tooling are **Apache-2.0**. Commercial use is permitted, including by vendors implementing the model in products, provided attribution is retained.

Assessments are **self-declared**. There is no certification scheme, and any claim of a "certified TID-CMM level" should be treated as marketing.

MITRE ATT&CK® is a registered trademark of The MITRE Corporation. This project is not affiliated with or endorsed by MITRE, NIST or SOC-CMM.

---

**Site** https://tid-cmm.com · **Contact** hello@tid-cmm.com · **Author** Reza Adineh

If you use TID-CMM, its datasets or its tooling, please cite it — see [CITATION.cff](CITATION.cff).
