# TID-CMM Public Data

This directory contains public datasets used by TID-CMM to support threat scoping, ATT&CK analysis, telemetry assurance and detection reasoning.

## Current files

| File | Purpose |
| --- | --- |
| `attack_techniques.csv` | MITRE ATT&CK Enterprise technique catalogue used for scoping and behavioural context. |
| `attack_actors.csv` | ATT&CK groups, campaigns, malware and tools with documented technique relationships. |
| `attack_analytics.json` | ATT&CK detection analytics and referenced telemetry/log-source requirements. |
| `attack_detection.csv` | Detection strategies associated with ATT&CK techniques. |
| `attack_log_sources.csv` | Normalised log-source index derived from ATT&CK detection content. |
| `telemetry_catalogue.yaml` | Public, product-neutral guidance for enabling telemetry capabilities used by the model. |

## Provenance

ATT&CK-derived content remains © The MITRE Corporation and is used under the ATT&CK Terms of Use. The repository adds TID-CMM-specific structure and derived indexes under the public licensing terms described in `LICENSE` and `NOTICE.md`.

Do not hand-edit generated ATT&CK datasets as a normal contribution. Mapping or source corrections should be raised as an issue so the derivation process can be corrected rather than creating a change that will disappear on the next regeneration.

## Model relationship

The data does not decide what matters to an organisation. TID-CMM first establishes the environment, threat profile, crown jewels and attack paths, then uses these datasets to determine which ATT&CK behaviours and telemetry requirements are in scope.

Canonical site and data/API documentation: https://tid-cmm.com