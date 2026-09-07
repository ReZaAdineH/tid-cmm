# TID-CMM Machine-Readable Model

## Current model

The canonical public model is **TID-CMM 1.6.0** (documents v1.6, released 6 September 2026). Its machine-readable
form is kept under [`1.6.0/`](1.6.0/) as byte-for-byte copies of the files the canonical site publishes at
https://tid-cmm.com/api/ — the model with its domains, sub-capabilities, level descriptors, weights, applicability
profiles, integrity constraints, tiers and the export schema. Their SHA-256 hashes are listed in
[`1.6.0/README.md`](1.6.0/README.md). When a copy here and the site differ, the site is the authority.

## Historical snapshot

`meta.yaml` and `domains/*.yaml` identify **TID-CMM 1.2.0** and are a historical snapshot preserved for
reproducibility, score-comparison research and understanding how constraints and descriptors evolved. They are not
the current model and must not be relabelled as such. `meta.yaml` carries the licence line of its own time; the
current terms are in the repository's `LICENSE` and at https://tid-cmm.com/licence/.

For current doctrine, constraints, assessment depth and public model interpretation, use the root README, `docs/`,
and the canonical site.
