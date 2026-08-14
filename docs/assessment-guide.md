# Running a TID-CMM assessment

A practical guide. The white paper has the reasoning; this is the procedure.

## 1. Decide what kind of assessment you are running

| Type | Effort | Confidence | Use when |
|---|---|---|---|
| Rapid self-assessment | Half a day, 2–3 people | Directional only | You need a baseline and a sense of where to look. **Do not report the number outside the team.** |
| Structured self-assessment | 2–3 days, 6–10 people, evidence gathered | Defensible internally | Annual planning, budget cases, board reporting with assumptions stated |
| Evidence-based assessment | 1–2 weeks, artefacts reviewed against each claimed level | Withstands challenge | Regulatory or contractual assurance, post-incident review, measuring investment |
| Independent assessment | 2–4 weeks including validation sampling | Highest | Third-party assurance, due diligence, or when internal scores have plateaued suspiciously |

Confidence rises with the cost of the evidence, not with the seniority of the assessor.

## 2. Get the right people in the room

| Domain | Who scores it |
|---|---|
| TI | Threat intelligence lead |
| TM | Security architect or threat modeller |
| DC | Detection platform / data engineering lead |
| DE | Detection engineering lead |
| AV | Purple team, red team or offensive security lead |
| AA | SOC manager and a senior analyst |
| IR | Incident response manager |
| GV | Security leadership |

If no one owns AV, that is itself a finding, and the domain is unlikely to score above 1.

Scores are **proposed by the owner and challenged by at least one other person**. The challenge question is always the same three words: *show me the artefact*.

## 3. Fix the scope before you score anything

Record, in the Setup tab or the setup page:

- entities, regions, business units and platforms **included**
- what is **excluded**, and who accepted that risk
- the threat profile document reference that drives the assessment
- the previous assessment date and score, if any

An assessment without a scope statement cannot be compared with anything, including itself six months later.

## 4. Define the in-scope ATT&CK technique set

This is the step most often skipped and most often regretted. Build it in this order:

1. **Filter by platform.** Remove techniques targeting platforms you do not operate. Objective, and usually removes 15–25%.
2. **Filter by threat profile.** Keep techniques used by your ranked actors and campaigns.
3. **Add back your attack-tree nodes.** A technique nobody has attributed to your adversaries but which sits on a short path to a crown jewel belongs in scope.
4. **Record every exclusion with a reason.**

**Never scope by ease of detection.** Excluding techniques because they are hard to see defeats the entire model.

In the browser tool, use the platform filter plus *Scope in by platform filter*. In the workbook, filter column E on the `ATT&CK Coverage` tab and set column F.

## 5. Score, in domain order

Score **TI → TM → DC → DE → AV → AA → IR → GV**. The order matters: scoring AV before the domains it caps produces defensive scoring in the earlier domains.

For each sub-capability:

- Read the question and all six descriptors before choosing.
- Score the **present tense**. Intent goes in the target column.
- Record the **evidence reference** as you go, not afterwards. A claim you cannot evidence in the session will not become evidenceable later.
- Mark **not applicable** only with a recorded rationale. It removes the item from the rollup entirely.

## 6. Read the constraint log before you read the score

The constraint log tells you where the organisation's self-image and its evidence diverge. It is usually the most useful output of the assessment, and it is what you take to leadership first.

## 7. Produce two reports

- **Engineering roadmap** — ranked by weighted impact, with the next-level descriptor as the acceptance criterion for each item.
- **Executive summary** — maturity band, validated coverage against the prioritised threat profile, known blind spots, and the risks accepted as a result. State clearly what is proven versus assumed.

## 8. Set the re-assessment date

Annual minimum, semi-annual if you are actively investing. **Keep the scope and the in-scope technique set stable between assessments.** If either changes, report both the like-for-like and the new-basis figures. A score that moves because the scope moved is worse than no score.

## Failure modes to watch for

| Failure | How it shows up | Counter |
|---|---|---|
| Scoring the intent | "We're doing that next quarter" scored as done | Present tense only |
| Scoring the tool | "We have a BAS platform" scored as L4 in AV.2 | Read the descriptor aloud — it asks about cadence, scope and drift alerting |
| Best-case scoring | The best business unit described as the estate | Score the scope as stated, or narrow the scope |
| Vocabulary drift | "Threat modeling" meaning a risk workshop | The level descriptors are the definition |
| Consensus averaging | Disagreement split down the middle | Record both scores and the evidence each cites; let the evidence decide |
| Assessment as appraisal | Owners defending scores | State that a low score is a funding argument. If that isn't true where you work, commission an independent assessment |


## Common questions

### How long does a detection maturity assessment take?

A rapid self-assessment takes half a day with two or three people and gives a directional
baseline. A structured assessment with evidence takes two to three days across six to ten people.
An evidence-based assessment, where artefacts are reviewed against each claimed level, takes one
to two weeks.

### Who should take part in a detection maturity assessment?

At minimum: threat intelligence, security architecture, the detection platform owner, detection
engineering, offensive security or purple team, SOC operations, incident response, and security
leadership for scope and sign-off. An assessment scored by one person is an opinion rather than an
assessment.

### How do I scope which ATT&CK techniques apply to my organisation?

Filter by the platforms you actually run, then by the techniques used by the threat actors your
threat profile ranks, then add anything appearing on a modelled attack path to a crown jewel.
Record every exclusion with a reason. Never scope by ease of detection.
