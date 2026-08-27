# TID-CMM Scoring and Integrity Constraints

Every TID-CMM sub-capability is scored from 0 to 5. Domain scores are weighted means of in-scope sub-capabilities; the overall score is the weighted mean of domain scores.

The important design rule is that **constraints can only lower a claim**. They exist to prevent maturity from being asserted without the prerequisites that make it real.

## Five integrity constraints

The current canonical model applies five constraints in the order:

**C3 → C5 → C4 → C2 → C1**

| ID | Constraint | Canonical intent |
| --- | --- | --- |
| C1 | Validation ceiling | No domain may exceed the Adversarial Validation domain + 1. A capability that has never been exercised cannot claim the highest maturity. |
| C2 | Visibility ceiling | Detection Engineering may not exceed Telemetry & Detection Coverage + 1. Detection cannot be more mature than the data it depends on. |
| C3 | Evidence rule | Scores of 4 or 5 require named evidence. Without evidence, high claims are capped. |
| C4 | Intent ceiling | Telemetry and Detection Engineering may not exceed max(Threat Intelligence, Threat Modeling) + 1. Sensors without threat and architectural intent produce noise, not defence. |
| C5 | Inherited intent ceiling | When the tool-generated threat profile is accepted unchanged, TI.2 is capped at level 2 because the organisation did not independently establish who matters. |

## Validated Coverage Score

TID-CMM reports validated coverage separately from domain maturity. The question is not simply whether a rule exists, but how far a relevant ATT&CK technique has progressed from no visibility to validated detection.

The in-scope ATT&CK set is derived from the organisation's environment, prioritised adversaries and attack paths. Reporting against all ATT&CK techniques regardless of relevance is treated as a vanity metric.

## Scenario coverage

A mature programme also asks whether detections contribute to complete attack scenarios leading to crown-jewel objectives. Technique coverage alone cannot prove that an attack path would be detected end to end.

Canonical scoring documentation: https://tid-cmm.com