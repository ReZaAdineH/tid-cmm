# Changelog

Changes to the **model and its datasets**. The assessment tool at
<https://tid-cmm.xyz> is versioned separately and is not covered here.

The format follows Keep a Changelog. A change to any level descriptor, weight or
sub-capability is a minor version at minimum, because it moves scores.

## [1.2.0] — 2026-08-15

### Changed

- **AA.7 Deception and adversary engagement** — level 4 now also expects breadcrumbs that
  lead credibly toward the decoys rather than leaving them to be stumbled upon, and a
  measured alert-noise rate. Evidence gains a measured noise rate including periods with
  no trips. Placement research is consistent that a decoy an adversary never encounters
  is worth less than a simple one they do.

### Unchanged

- 8 domains, 58 sub-capabilities, 348 level descriptors. Domain weights, sub-capability
  weights and the four integrity constraints are unchanged, so **scores from 1.1.0 remain
  directly comparable**.

## [1.1.0] — 2026-08-12

### Added

- Fourth integrity constraint **C4 — intent ceiling**: DC and DE may not exceed
  max(TI, TM) + 1. Sensors and content without architectural intent produce noise.
- Maturity tiers with entry gates, so a high weighted score alone does not buy a tier.
- Applicability profiles — essential, standard, comprehensive — so a small organisation is
  not assessed against the burden of a large regulated one.
- Detection classes: decisive, corroborative, and hunting or context.

### Changed

- Expanded from 53 to 58 sub-capabilities, and from three constraints to four.
- ATT&CK alignment moved to Enterprise v19.2, which restructured detection into strategies
  and analytics referencing concrete log sources.

## [1.0.0] — 2026-08-10

- First public version: 8 domains, 53 sub-capabilities, three integrity constraints.
