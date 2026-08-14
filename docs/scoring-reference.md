# Scoring reference

## Rollup

```
domain_score   = Σ(sub_weight × sub_score) / Σ(sub_weight)     over in-scope sub-capabilities
overall_score  = Σ(domain_weight × domain_score) / Σ(domain_weight)
```

Sub-capabilities marked **not applicable** are excluded from both numerator and denominator. Scoping something out neither helps nor harms the score — it removes it.

## Order of operations

1. **C3** at sub-capability level — a score of 4 or 5 with no named evidence becomes 3.
2. Compute raw domain scores.
3. **C2** — cap `DE` at `DC + 1`.
4. **C1** — cap every other domain at `adjusted AV + 1`.
5. Compute the overall score from adjusted domain scores.
6. Report the unadjusted score, the adjusted score, and every adjustment.

## The three constraints

| ID | Name | Rule | Why |
|---|---|---|---|
| C1 | Validation ceiling | No domain > AV + 1 | An untested capability is an assumed capability. The one-level margin acknowledges a capability can be well-built before it is validated — but only just. |
| C2 | Visibility ceiling | DE ≤ DC + 1 | Detection logic cannot outperform its inputs. |
| C3 | Evidence rule | 4 or 5 without a named artefact → 3 | In any process where an unevidenced claim scores the same as an evidenced one, assertion drives out evidence. |

`strict: false` disables all three. Use it only to see the raw self-assessment; never report a non-strict score externally.

## Bands

| Score | Band | In practice |
|---|---|---|
| 0.00–0.99 | L0 Absent | A build project, not an improvement project |
| 1.00–1.99 | L1 Ad hoc | Capability lives in individuals; it will not survive their departure |
| 2.00–2.99 | L2 Repeatable | The most populated band, and where spending most often outruns capability |
| 3.00–3.99 | L3 Threat-Informed | A credible target for most organisations |
| 4.00–4.99 | L4 Measured & Validated | Realistic only with a standing validation function |
| 5.00 | L5 Adaptive | Rare. Treat with scepticism unless the evidence is exceptional |

## Validated Coverage Score

```
VCS = Σ(status) / (3 × count(in-scope techniques))
```

| Status | Meaning | Requires |
|---|---|---|
| 0 | No telemetry | The activity generates no record you collect |
| 1 | Telemetry only | Data exists and is queryable; nothing alerts |
| 2 | Detection logic exists | A rule or analytic is deployed and healthy, but unproven |
| 3 | Validated by emulation | Behaviour executed, detection observed to fire, within the recency window |

Always report the in-scope count beside the score. **Status 3 expires** — a result older than your defined review window drops to 2.

Report alongside the domain scores, never instead of them.

## Prioritisation

```
impact = (domain_weight / 100) × (sub_weight / 100) × gap_to_target × 1000
```

Mechanical by design: it prevents the roadmap being driven by whoever argued hardest. It produces the counter-intuitive but usually correct result that a two-level gap in a heavily weighted sub-capability outranks a four-level gap in a light one.

The ranking is a starting point, not an instruction. Dependencies matter — improving DE before fixing DC wastes effort, which is why C2 exists. Read the constraint log alongside the roadmap.

## Setting targets

Set targets **per domain**, not globally. Defensible target for a well-resourced enterprise: 3.5–4.0 overall, with AV at 4.0+ so it stops being the binding constraint. For a smaller organisation, 2.5–3.0 over an honest, narrow in-scope set is a stronger position than 3.5 over a scope chosen to flatter.

Level 5 is not a target for most organisations. Treating it as one produces theatre.
