# Contributing

This repository holds the model and its datasets. The most useful contribution is not a
correction — it is a **counter-example**.

## What is most wanted

**Descriptor challenges.** If a level descriptor does not match what you see in practice,
open an issue saying which sub-capability, which level, and what you have actually
observed. A descriptor that reads well and does not survive contact with a real programme
is a defect.

**Weight arguments.** Domain and sub-capability weights are a judgement. They are exposed
as editable parameters precisely so you can disagree with them. Argue for a different one
with reasoning, not preference.

**Crosswalks.** DORA, NIS2, PCI DSS 4.0, CMMC and sector-specific frameworks are all
welcome. Map at sub-capability level, not domain level.

**Anonymised assessment data**, if your organisation is willing. Sector benchmarking is
only possible with it, and there is no benchmark today.

## What changes a version

Any change to a level descriptor, a weight, a sub-capability or a constraint moves scores,
so it is a minor version at minimum and goes in `CHANGELOG.md` with the reasoning. Adding
a crosswalk or fixing prose is a patch.

## Datasets

Files in `data/` are derived from MITRE ATT&CK and regenerated on each ATT&CK release.
Do not hand-edit them; raise an issue instead, because a manual edit will be overwritten
and the change will be lost.

## Scope

The assessment tool is not developed here. Bugs in the tool at <https://tid-cmm.xyz>
belong in an email to hello@tid-cmm.com rather than an issue on this repository.
