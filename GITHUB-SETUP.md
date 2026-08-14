# Publishing TID-CMM on GitHub

Everything here is written and validated. This is the order to do it in, and the
decisions worth making deliberately.

---

## 1. Repository name and account

Your account is **`ReZaAdineH`**. The site currently links to `github.com/rezaadineh/tdmm`,
which does not exist — fix the link or the repo, but do not ship both.

**Recommended: `ReZaAdineH/tid-cmm`.**

`tid-cmm` matches the domain, the model name, the white paper and every search anyone will
run. `tdmm` is the older name and is now ambiguous with the tier model inside TID-CMM.

If you want to keep `tdmm` alive, create it as an empty repo whose README points at
`tid-cmm` — GitHub redirects renamed repos automatically, so renaming an existing one is
also safe.

**Repository description** (the one line under the name — it is indexed):

> Open capability maturity model for threat-informed detection. Measure ATT&CK coverage
> honestly, find what your telemetry cannot see, get a ranked plan. Free tool, no account.

**Topics** — GitHub topic pages rank, and these are how people browse:

```
mitre-attack  detection-engineering  threat-detection  maturity-model  security-operations
soc  threat-informed-defense  purple-team  threat-hunting  detection-as-code
siem  blue-team  cybersecurity  attack-navigator  telemetry
```

**Settings to turn on:** Issues, Discussions, Sponsors (optional), and under Security:
Private vulnerability reporting, Dependabot alerts, and Secret scanning.

**Social preview image:** upload `tools/site/og-image.png` under Settings → General. Without
it, shared repo links render as a grey placeholder.

---

## 2. What to commit, and what not to

Source is about **2 MB**. The build output is **17 MB** and fully reproducible.

**Commit:**

```
model/          the model itself — this is the substance of the repository
data/           the ATT&CK-derived datasets (1.4 MB, and the most citable thing here)
tidcmm/         Python loader, scoring engine, scoping engine, CLI
tools/          build scripts, the site source, the app template
tests/          44 tests
docs/           assessment guide, scoring reference
assessments/    blank template and worked example
README.md  CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md  CHANGELOG.md
CITATION.cff  LICENSE  LICENSE-CODE  Makefile  requirements.txt
.github/  .gitignore  .gitattributes
```

**Do not commit `build/`.** It is in `.gitignore`. Binaries go on Releases instead, so
clones stay small and there is no chance of a stale PDF sitting next to a current model.

The one judgement call: `data/*.csv` is generated, but **commit it anyway**. Those files are
the reason people will find and cite this repository, and requiring a build step to get them
would defeat that. They are tagged `linguist-generated` so they do not distort the language
statistics or clutter diffs.

---

## 3. Releases

Tag `v1.1.0` and attach:

- `TID-CMM-White-Paper-v1.1.pdf`
- `TID-CMM-Self-Assessment-v1.1.xlsx`
- `TID-CMM-Worked-Example-v1.1.xlsx`
- `tid-cmm-assessment.html` — the offline tool, the single most useful attachment
- `tid-cmm-site-upload.zip` — so anyone can self-host the whole thing
- `model.json`

Release notes: lift the v1.1 section from `CHANGELOG.md`, and lead with the Sysmon figure.
A release people actually read is one that opens with a fact.

---

## 4. Files now in the repo, and why each earns its place

| File | Why it matters |
|---|---|
| **CITATION.cff** | GitHub renders a "Cite this repository" button and Zenodo reads it. Turns informal mentions into formal citations, which is how a model gets adopted in regulated industries. |
| **SECURITY.md** | States the design commitments as testable claims — no network requests, no cookies, imported data sanitised — and names the one accepted risk (`unsafe-inline`). Publishing a known limitation is more credible than implying there are none. |
| **CODE_OF_CONDUCT.md** | Short and specific to this project: *argue with the model, not the person*. |
| **.github/ISSUE_TEMPLATE/** | Four templates. The descriptor-challenge one is the important one — it asks for a counter-example and the organisational context, which is exactly what makes a challenge usable. |
| **PULL_REQUEST_TEMPLATE.md** | Enforces the model's own rules at review time: validation passes, no product names, level 4/5 names an artefact. |
| **.gitattributes** | Marks generated data so GitHub does not report this as a "CSV project", and forces LF endings so Windows contributors do not produce whole-file diffs. |
| **dependabot.yml** | Monthly, limited to three PRs. Enough to stay patched without noise. |

---

## 5. Two workflows

**`ci.yml`** runs on every push and PR:

- validates the model, runs the 44 tests
- rebuilds every deliverable from source — catches the case where the model changes but the
  workbook generator silently breaks
- **`node --check` on the extracted tool JavaScript.** A syntax error in that inline script
  renders a blank page rather than erroring visibly; this exact failure has already happened
  once during development, so it is now a gate
- asserts the site makes no external requests
- asserts no product names crept into descriptors
- uploads the built artefacts, so a PR reviewer can download the workbook

**`attack-refresh.yml`** runs monthly. It checks whether MITRE has published a newer ATT&CK
Enterprise release and opens an issue with the refresh checklist if so. Coverage computed
against a different ATT&CK version is not comparable, so this drift must be visible rather
than discovered a year later.

---

## 6. README

The existing `README.md` is the repository's landing page and its most-read document. Before
publishing, check three things:

1. Counts say **58 sub-capabilities / 348 descriptors** and the constraints table lists
   **C1–C4** — it was written at 53 and three constraints
2. Every `build/…` path is replaced with a Release link, since `build/` is not committed
3. Badges point at the real repository

Consider adding, high up:

> **423 techniques — 89% of all Windows techniques in ATT&CK Enterprise v19.2 — have
> detection analytics that reference Sysmon.** For 20 of them it is the only source
> referenced. If you do not run it or an equivalent, that is not a gap in your rule set.

That single block is the most linkable thing in the repository.

---

## 7. After it is live

- **Pin the repository** on your GitHub profile
- **Enable Discussions** and seed one thread: *"Where do the weights feel wrong to you?"* — a
  repository with a real conversation in it looks alive, and the weights are genuinely the
  part most worth challenging
- **Submit to `awesome-detection-engineering`** — a legitimate, durable link and the exact
  audience
- **Archive a release to Zenodo** for a DOI, once, if you want academic citability. It reads
  `CITATION.cff` automatically
- Add the repository link to your Medium profile and LinkedIn

---

## 8. What not to do

- **Do not commit `build/`** just to make files browsable. Releases exist for that.
- **Do not add a `gh-pages` site.** The Cloudflare site is the canonical one; a second copy
  splits search authority and will drift.
- **Do not accept descriptor changes without a counter-example.** The model's credibility
  rests on descriptors being observable, and "someone asked for it" is not evidence.
- **Do not let the repo and the site disagree.** Both are generated from `model/`, so
  regenerate and redeploy in the same change.
