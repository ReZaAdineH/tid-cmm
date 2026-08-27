# Telemetry Engineering and Telemetry Assurance

A detection rule cannot compensate for evidence that does not exist.

TID-CMM therefore treats telemetry as an engineered capability. For every relevant adversary behaviour, the assessment asks whether the required evidence is available across enough of the estate, whether the source is healthy, and whether the data is usable by detection logic.

The canonical public site bands technique visibility as:

- **Assured** — the required evidence is available and sufficiently covered to support the detection claim.
- **Partial** — useful evidence exists, but coverage or completeness is incomplete.
- **Weak** — evidence is present but structurally insufficient or unreliable for the behaviour.
- **Blind** — the organisation lacks the evidence needed to observe the behaviour.

A missing data source is not merely a rule-writing problem. It becomes a **Telemetry Engineering requirement**.

The public telemetry catalogue in `data/telemetry_catalogue.yaml` documents ways to enable high-value sources without turning TID-CMM into a product recommendation model.

Canonical telemetry-assurance guidance: https://tid-cmm.com