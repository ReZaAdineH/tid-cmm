# TID-CMM — Threat-Informed Detection Capability Maturity Model

**Version 1.2.0** · 8 domains · 58 sub-capabilities · 348 level descriptors ·
aligned to MITRE ATT&CK Enterprise v19.2

Most detection programmes can tell you how many rules they run and how many alerts they
closed. Neither measures whether they would see the adversaries most likely to attack
them. TID-CMM measures that: whether detection is driven by adversary behaviour, whether
the telemetry exists to see it, and whether any of it has been proven to work.

This repository holds **the model and its datasets**. The assessment tool that implements
them is free to use at **<https://tid-cmm.xyz>** — no account, no email address, and
nothing you enter leaves your browser.

---

## What is here

| Path | Contents |
| --- | --- |
| `model/meta.yaml` | Model definition: levels, domain weights, maturity tiers and their entry gates, the four integrity constraints, applicability profiles, environment archetypes |
| `model/domains/*.yaml` | Eight domains. Every sub-capability carries a weight, an applicability profile, the question it answers, all six level descriptors, the evidence that substantiates a claim, and crosswalks to NIST CSF 2.0 and SOC-CMM |
| `data/attack_techniques.csv` | ATT&CK Enterprise v19.2 — 697 techniques with tactics, platforms, data components and mitigations |
| `data/attack_actors.csv` | 1,057 groups, campaigns, malware families and tools with the techniques each uses |
| `data/attack_analytics.json` | 1,745 ATT&CK detection analytics with the concrete log sources they require |
| `data/attack_detection.csv` | Detection strategies per technique |
| `data/attack_log_sources.csv` | Normalised log source index |
| `data/telemetry_catalogue.yaml` | How to enable the sources that carry the bulk of the analytics: channels, tool class, free route, effort and volume |

## The eight domains

| ID | Domain | Weight | The question it answers |
| --- | --- | --- | --- |
| **TI** | Threat Intelligence & Adversary Prioritisation | 12% | Who are we defending against, and how do we know? |
| **TM** | Threat Modeling & Attack Path Analysis | 12% | What do their behaviours look like against our architecture? |
| **DC** | Telemetry & Detection Coverage | 14% | Can we see the activity at all? |
| **DE** | Detection Engineering | 16% | Do we build, test and maintain detection like engineers? |
| **AV** | Adversarial Validation & Emulation | 14% | Have we proven any of it works? |
| **AA** | Analytics, Automation & Hunting | 12% | Does detection output become a decision at operational tempo? |
| **IR** | Incident Response & Recovery | 10% | Can we act on what we detect? |
| **GV** | Governance, Metrics & Continuous Improvement | 10% | Is this directed, measured and sustainable? |

## The four integrity constraints

A maturity self-assessment flatters itself unless something stops it. These are applied
mechanically at scoring time, in the order **C3 → C4 → C2 → C1**, each capping the thing
it depends on. A ceiling may only ever lower a score.

| ID | Name | Rule |
| --- | --- | --- |
| **C1** | Validation ceiling | No domain may be scored above the AV domain score + 1. |
| **C2** | Visibility ceiling | DE (Detection Engineering) may not exceed DC (Telemetry & Detection Coverage) + 1. |
| **C3** | Evidence rule | Any score of 4 or 5 requires a named artefact recorded in the evidence field. |
| **C4** | Intent ceiling | DC and DE may not exceed max(TI, TM) + 1. |

The full scoring arithmetic — the weighted rollup, the order of application, the Validated
Coverage Score and the prioritisation formula — is published at
<https://tid-cmm.xyz/scoring>, and the model is served as JSON at
<https://tid-cmm.xyz/api/model.json>.

## Using it

Read the model here, or run the assessment at <https://tid-cmm.xyz/assess>. The tool
derives an in-scope ATT&CK set from your environment, your prioritised threat actors and
your attack paths — typically 150 to 250 techniques rather than all 697 — then
computes which of those behaviours your telemetry cannot see, and what to enable.

A worked example, the white paper, the Excel workbook and an offline copy of the tool are
at <https://tid-cmm.xyz/downloads>.

## Licence

The **model content and datasets in this repository** are licensed
[CC-BY-4.0](LICENSE). Use them commercially, including inside products, provided
attribution is retained.

The **assessment tool** at tid-cmm.xyz is free to use for any purpose, including
commercial assessment work. It is not open source and is not licensed for
redistribution or derivative tooling.

MITRE ATT&CK® is a registered trademark of The MITRE Corporation. ATT&CK content in
`data/` is © The MITRE Corporation and used under the
[ATT&CK Terms of Use](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/).
This project is not affiliated with or endorsed by MITRE, NIST or SOC-CMM.

## Contributing

Descriptors, weights and crosswalks are open to challenge. If a level descriptor does not
match what you see in practice, open an issue with the counter-example — that is more
useful than a correction without one. See [CONTRIBUTING.md](CONTRIBUTING.md), and
[CHANGELOG.md](CHANGELOG.md) for what has moved and why.

---

Created and maintained by **Reza Adineh**. TID-CMM is the detection component of UTIOM,
the Unified Threat-Informed Operations Model.
