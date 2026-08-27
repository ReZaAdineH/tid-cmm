# Contributing to TID-CMM

TID-CMM is intended to be argued with. The most useful contribution is not a generic correction — it is a **counter-example, measurement or authoritative mapping correction** that makes the model harder to game and more useful in real security operations.

Canonical site: https://tid-cmm.com

## What is most wanted

### Descriptor challenges

If a level descriptor does not match what you see in practice, identify the exact sub-capability and level, describe the counter-example and explain why two competent assessors could reach the wrong conclusion from the current wording.

### Weight and constraint arguments

Domain/sub-capability weights and integrity-constraint calibration are judgements. Challenge them with reasoning about what behaviour the model would incentivise or suppress, and ideally with assessment data.

### Crosswalks

DORA, NIS2, PCI DSS 4.0, CMMC and sector-specific mappings are welcome. Prefer sub-capability-level mapping over broad domain equivalence.

### Anonymised assessment data

Benchmarking requires contributed data. If your organisation is willing, remove identifiers and sensitive detail while preserving useful context such as sector, size band, domain scores, applicability profile and in-scope technique count.

### Telemetry catalogue improvements

The catalogue intentionally names capabilities and enablement routes rather than recommending vendors. New entries or corrections should retain that technology-neutral approach.

## Model-change rules

- Descriptors must be observable.
- Level 3 is the threat-informed step.
- Level 4 requires measurement/validation.
- Level 5 requires an adaptive closed loop.
- High-level claims need plausible evidence artefacts.
- Product names do not belong in maturity requirements.
- Any change that can move a score must be versioned and explained in `CHANGELOG.md`.

## Generated datasets

ATT&CK-derived files in `data/` should not be hand-edited as the normal fix path. Raise a data/mapping issue so the source or derivation can be corrected and the next regeneration preserves the fix.

## Tool scope

This repository is the open model/data/community repository. The free assessment tool is available at https://tid-cmm.com and is not licensed for redistribution or derivative tooling. Security findings affecting the tool must be reported privately under `SECURITY.md`.

## Community channels

Use Discussions for questions, implementation stories, research and early ideas. Use Issues for concrete model/data/documentation changes. See `COMMUNITY.md` and `CODE_OF_CONDUCT.md`.
