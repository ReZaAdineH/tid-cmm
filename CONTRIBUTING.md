# Contributing to TID-CMM

The model is meant to be argued with. Nothing in it is settled by authority.

## What is most useful

1. **Descriptor challenges.** If a level descriptor does not match what you see in practice, open an issue with the counter-example. "L4 of DE.5 is unrealistic because precision cannot be measured when case closure data is this poor" is a better contribution than a typo fix.
2. **Crosswalks.** DORA, NIS2, PCI DSS 4.0, CMMC, HIPAA Security Rule, sector-specific frameworks. Add them under `crosswalk:` in the relevant sub-capability.
3. **Weight arguments.** Domain and sub-capability weights are a judgement. Argue for a different one with reasoning about what the change would cause an organisation to do differently.
4. **Anonymised assessment data.** Sector benchmarks are only possible if people share. Strip identifiers; keep sector, size band, domain scores and in-scope technique count.
5. **Tooling.** Additional exporters (ATT&CK Navigator layers, Sigma repository integration, SIEM-specific coverage importers) are welcome.

## Ground rules for model changes

- **Descriptors must be observable.** If two competent assessors could not agree whether an organisation meets it, rewrite it. "Adequate threat intelligence" is not a descriptor; "PIRs decomposed into SIRs and EEIs, each tied to a named decision-maker" is.
- **Level 3 is the threat-informed step.** Do not describe activity at L3 that is not driven by a prioritised adversary profile.
- **Level 4 requires measurement, Level 5 requires a closed loop.** Keep the ladder consistent across all 53 sub-capabilities.
- **Every level 4 and 5 descriptor needs a plausible evidence artefact** in the `evidence:` list. If you cannot name one, the descriptor is aspirational, not assessable.
- **No product names.** The model scores behaviour, not procurement.

## Process

```bash
git checkout -b descriptor/DE-4-testing
$EDITOR model/domains/DE.yaml
python -m tidcmm validate      # must pass
python -m pytest tests -q      # must pass
make all                       # regenerate deliverables
```

Open a pull request describing:

- what the current descriptor says
- what it should say
- the practice you have observed that justifies the change

## Versioning

- **Patch** (`1.0.x`) — typos, crosswalk additions, tooling fixes. Scores are unaffected.
- **Minor** (`1.x.0`) — descriptor rewording that could change a score, new crosswalks, new sub-capability evidence examples. Assessments should state the version used.
- **Major** (`x.0.0`) — added or removed sub-capabilities, changed weights, changed constraints. Not comparable with prior assessments without restating.

Every assessment output records the model version. Do not compare scores across a major version without saying so.

## ATT&CK releases

`data/attack_techniques.csv` is regenerated on each ATT&CK release. Regenerating changes technique counts and therefore in-scope sets. Bump the `alignment.attack` block in `model/meta.yaml`, regenerate, and note the diff in `CHANGELOG.md`.

## Provenance of published files

Nothing shipped from this repository names the tools used to author it. That includes
document properties, not just visible text — `openpyxl` and friends stamp themselves into
`docProps/app.xml` unless told otherwise, and editor lock files carry the build account name.

`python tools/check_provenance.py` enforces this and runs in CI. It checks visible text,
Office document metadata, and stray temporary files.

One deliberate exemption: files derived from MITRE ATT&CK are not checked for vocabulary.
ATT&CK names real malware (GeminiDuke), cites real research, documents LLM abuse as technique
T1683, and publishes a campaign called "Anthropic AI-orchestrated Campaign" (C0062). That is
threat intelligence, not provenance, and removing it would corrupt the dataset.

If you add a generator, set the author metadata explicitly and re-run the check.

## Code of conduct

Argue with the model, not with the person. Assume the other party has seen a different set of organisations than you have, because they probably have.
