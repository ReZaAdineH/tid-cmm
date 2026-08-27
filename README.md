# TID-CMM — Threat-Informed Detection Capability Maturity Model

**Would you actually see the adversaries most likely to attack you?**

**Canonical model: 1.5.0 · released 20 August 2026**  
**Documents: v1.4**  
**MITRE ATT&CK Enterprise: v19.2 · 697 techniques**  
**Canonical website: https://tid-cmm.com**  
**Assessment: https://tid-cmm.com/assess**

TID-CMM is an open, evidence-driven capability maturity model for **threat-informed detection engineering**. It measures whether detection is driven by relevant adversary behaviour, whether the telemetry exists to observe that behaviour, and whether the claimed capability has actually been proven to work.

**Focus areas:** Detection Engineering · Threat-Informed Defense · MITRE ATT&CK · Threat Intelligence · Threat Modeling · Attack Paths · Telemetry Engineering · Telemetry Assurance · Detection Validation · Purple Teaming · Threat Hunting · SOC Maturity · Security Operations

TID-CMM is the **detection measurement module of UTIOM**, the Unified Threat-Informed Operations Model. UTIOM remains the overarching operating model; TID-CMM adds measurement depth to the engineering and detection capability already defined by UTIOM. It does not replace UTIOM and it does not add a new UTIOM lifecycle phase.

> **Relevant adversaries → crown jewels and attack paths → in-scope ATT&CK behaviours → required telemetry → assured visibility → engineered detections → adversarial validation → measurable improvement.**

---

## What TID-CMM measures

The model contains **8 domains, 58 sub-capabilities and 348 explicit level descriptors**, each scored from 0 to 5.

| ID | Domain | Weight | Sub-caps | Core question |
| --- | --- | ---: | ---: | --- |
| **TI** | Threat Intelligence & Adversary Prioritisation | 12% | 6 | Who are we defending against, and how do we know? |
| **TM** | Threat Modeling & Attack Path Analysis | 12% | 7 | What do their behaviours look like against our architecture? |
| **DC** | Telemetry & Detection Coverage | 14% | 6 | Can we see the activity at all? |
| **DE** | Detection Engineering | 16% | 10 | Do we build, test and maintain detection like engineers? |
| **AV** | Adversarial Validation & Emulation | 14% | 8 | Have we proven any of it works? |
| **AA** | Analytics, Automation & Hunting | 12% | 8 | Does detection output become a decision at operational tempo? |
| **IR** | Incident Response & Recovery | 10% | 6 | Can we act on what we detect? |
| **GV** | Governance, Metrics & Continuous Improvement | 10% | 7 | Is this directed, measured and sustainable? |

The IR domain deliberately measures the **detection-to-response interface**. Full response capability — containment authority, response engineering, response tempo, recovery and exercising — is measured by **TIR-CMM**: https://tir-cmm.com.

---

## Five integrity constraints

TID-CMM refuses to let a self-assessment flatter itself. The current model applies five ceilings mechanically in the order **C3 → C5 → C4 → C2 → C1**. A ceiling may only lower a score.

| ID | Constraint | Rule |
| --- | --- | --- |
| **C1** | Validation ceiling | No domain may exceed the AV domain score + 1. |
| **C2** | Visibility ceiling | Detection Engineering may not exceed Telemetry & Detection Coverage + 1. |
| **C3** | Evidence rule | A score of 4 or 5 requires a named evidence artefact; otherwise it is capped at 3. |
| **C4** | Intent ceiling | DC and DE may not exceed max(TI, TM) + 1. |
| **C5** | Inherited intent ceiling | TI.2 may not exceed level 2 when the tool-generated threat profile is accepted unchanged. |

The point is causal integrity: **strategy directs telemetry, telemetry carries detection, and validation proves it**.

---

## Assessment depth

The same 58-sub-capability model can be used at three evidence depths:

- **Rapid self-assessment** — approximately half a day; directional; evidence ceiling means the result should remain an internal baseline.
- **Structured self-assessment** — approximately 2–3 days; named artefacts support higher claims and a result defensible for internal planning.
- **Evidence-based assessment** — approximately 1–2 weeks; independent review of artefacts and validation recency; intended for assurance, due diligence and external challenge.

Assessments are self-declared. **There is no TID-CMM certification scheme.** A claim of a “certified TID-CMM level” is not an official TID-CMM designation.

---

## Repository contents

This repository is the **public model, open-data and community repository**.

| Path | Contents |
| --- | --- |
| `model/` | Versioned model source, domain definitions and schemas. Historical source snapshots may remain for reproducibility; the canonical current model version is stated above and on https://tid-cmm.com. |
| `data/` | ATT&CK-derived datasets and the telemetry catalogue. See [`data/README.md`](data/README.md). |
| `docs/` | Search- and citation-friendly public knowledge base mirroring the canonical website. |
| `.github/` | Contribution, community, discussion and repository-integrity automation. |

The canonical machine-readable endpoints are documented at https://tid-cmm.com/developers/api/.

---

## Public knowledge base

Start with [`docs/README.md`](docs/README.md). It covers:

- why TID-CMM exists;
- the eight domains and 58 sub-capabilities;
- maturity levels and programme tiers;
- five integrity constraints;
- threat scoping and C5;
- telemetry assurance;
- Validated Coverage Score;
- evidence requirements and assessment depth;
- relationship to MITRE ATT&CK;
- relationship to UTIOM and TIR-CMM;
- scoring, applicability profiles and detection classes;
- limitations, licensing and FAQ.

For AI/search discovery, see [`llms.txt`](llms.txt) and the terminology/entity definitions in the knowledge base.

---

## Open model, open data, free assessment tool

The licensing boundary follows the canonical site:

- **Open Model** — CC BY 4.0. Commercial use, adaptation and product integration are permitted with attribution.
- **Open Data** — CC BY 4.0, while MITRE ATT&CK content remains © The MITRE Corporation under the ATT&CK Terms of Use.
- **Free Assessment Tool** — free to use for any purpose, including paid client assessment work, but **not licensed for redistribution, rebranding or derivative tooling**.

The assessment tool source is therefore intentionally not published as part of this repository.

See [`LICENSE`](LICENSE), [`NOTICE.md`](NOTICE.md) and https://tid-cmm.com/licence/.

---

## Community

TID-CMM is intended to be challenged with evidence.

Especially useful contributions include:

- counter-examples to level descriptors;
- evidence that a weight or constraint is miscalibrated;
- telemetry-catalogue additions;
- ATT&CK mapping corrections;
- NIS2, DORA, PCI DSS, CMMC and sector crosswalks;
- anonymised assessment data suitable for future benchmarking;
- implementation stories from internal, outsourced and hybrid SOCs.

Read [`COMMUNITY.md`](COMMUNITY.md), [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

**Security findings must not be posted publicly.** See [`SECURITY.md`](SECURITY.md).

---

## Framework family

- **UTIOM — Unified Threat-Informed Operations Model** — https://utiom.de
- **TID-CMM — Detection capability depth** — https://tid-cmm.com
- **TIR-CMM — Response capability depth** — https://tir-cmm.com
- **RSMM — Realistic SIEM Maturity Model** — https://rsmm.rezaadineh.com/
- **KEVMAP — exploited-vulnerability and exposure context** — https://kevmap.io

These are related instruments, not additional UTIOM lifecycle phases.

---

## Citation

Use [`CITATION.cff`](CITATION.cff). In prose:

> Adineh, R. (2026). *TID-CMM: Threat-Informed Detection Capability Maturity Model* (v1.5.0). https://tid-cmm.com

---

Created and maintained by **Reza Adineh**.  
https://rezaadineh.com

**Think smarter, Stay Secure.**

MITRE ATT&CK® is a registered trademark of The MITRE Corporation. This project is independent and is not affiliated with or endorsed by MITRE, NIST or SOC-CMM.
