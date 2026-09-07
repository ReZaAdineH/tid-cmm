# TID-CMM Public Data

This directory contains public datasets used by TID-CMM to support threat scoping, ATT&CK analysis, telemetry assurance and detection reasoning.

## Current files

| File | Purpose |
| --- | --- |
| `attack_techniques.csv` | MITRE ATT&CK Enterprise technique catalogue used for scoping and behavioural context. |
| `attack_actors.csv` | ATT&CK groups, campaigns, malware and tools with documented technique relationships. |
| `actor_sectors.yaml` | Mapping from ATT&CK actors, campaigns and groups to the sectors they are documented targeting, used to derive a suggested threat profile from an organisation's declared sector and regions. |
| `attack_analytics.json` | ATT&CK detection analytics and referenced telemetry/log-source requirements. |
| `attack_detection.csv` | Detection strategies associated with ATT&CK techniques. |
| `attack_log_sources.csv` | Normalised log-source index derived from ATT&CK detection content. |
| `telemetry_catalogue.yaml` | Public, product-neutral guidance for enabling telemetry capabilities used by the model. |

The six public reference datasets are: ATT&CK techniques, ATT&CK actors, actor-sector
mappings, ATT&CK detection mappings, the telemetry catalogue, and ATT&CK log sources
(`attack_analytics.json` is a seventh, derived index kept alongside them - see Provenance
below). These are also published as release assets on the repository's Releases page,
where the site's Resources page links five of them (all but `attack_log_sources.csv` and
`attack_analytics.json`) at `releases/latest/download/<filename>`.

## Provenance

ATT&CK-derived content remains © The MITRE Corporation and is used under the ATT&CK Terms of Use. The repository adds TID-CMM-specific structure and derived indexes under the public licensing terms described in `LICENSE` and `NOTICE.md`.

Do not hand-edit generated ATT&CK datasets as a normal contribution. Mapping or source corrections should be raised as an issue so the derivation process can be corrected rather than creating a change that will disappear on the next regeneration.

## Model relationship

The data does not decide what matters to an organisation. TID-CMM first establishes the environment, threat profile, crown jewels and attack paths, then uses these datasets to determine which ATT&CK behaviours and telemetry requirements are in scope.

Canonical site and data/API documentation: https://tid-cmm.com