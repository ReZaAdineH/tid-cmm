# Pushing this repository

The zip contains a git repository with one commit already made, authored as
`Reza Adineh <hello@tid-cmm.com>`, and tagged `v1.1.0`. You do **not** need to `git init`.

`ReZaAdineH/tid-cmm` already exists as a private draft with earlier commits. This
history is unrelated to it, so the push has to be forced. Step 1 keeps the old
content safe first.

---

## 1. Back up the existing draft (do this first)

Force-pushing discards the old commits from `main`. Keep a copy before you do.

```bash
cd ~/Desktop
git clone https://github.com/ReZaAdineH/tid-cmm.git tid-cmm-old-draft
```

That folder is now a complete copy of all 7 commits, on your Mac, whatever happens next.

Optionally also keep the old history visible on GitHub as a branch:

```bash
cd ~/Desktop/tid-cmm-old-draft
git push origin main:draft-2024
```

The old work then lives at `github.com/ReZaAdineH/tid-cmm/tree/draft-2024` permanently.

## 2. Unpack the new repository

```bash
cd ~/Desktop
unzip tid-cmm-repo.zip        # creates ~/Desktop/tid-cmm
cd tid-cmm
git log --oneline             # expect exactly one commit: TID-CMM v1.1.0
```

If your global git identity differs from the commit author and you want your own
identity on it instead:

```bash
git commit --amend --reset-author --no-edit
git tag -f -a v1.1.0 -m "TID-CMM v1.1.0"
```

## 3. Point it at GitHub and force-push

```bash
git remote add origin https://github.com/ReZaAdineH/tid-cmm.git
git push --force origin main
git push origin v1.1.0
```

If you use SSH keys rather than HTTPS, use
`git@github.com:ReZaAdineH/tid-cmm.git` as the remote instead.

**If the push is rejected**, `main` is a protected branch. Settings → Branches →
remove the protection rule, push, then reinstate it.

**If you are asked for a password**, GitHub no longer accepts account passwords over
HTTPS. Either install the CLI (`brew install gh` then `gh auth login`, which stores a
credential for you), or create a personal access token at
github.com/settings/tokens and paste that as the password.

## 4. Delete the leftover draft files

The force-push replaces `main` entirely, so the old files disappear on their own.
Confirm on github.com/ReZaAdineH/tid-cmm that the root now shows `model/`,
`tidcmm/`, `tools/`, `data/`, `docs/`, `tests/` and not the old
`TDMM_*` / `tdmm_repo.zip` files. If any survive, you pushed without `--force`.

## 5. Make it public and configure it

**Settings → General → Danger Zone → Change visibility → Public.**

**About** (the gear icon on the repository home page)

- Description: *Open capability maturity model for threat-informed detection. Measure
  ATT&CK coverage honestly, find what your telemetry cannot see, get a ranked plan.
  Free tool, no account.*
- Website: `https://tid-cmm.com`
- Topics:

```
mitre-attack detection-engineering threat-detection maturity-model security-operations
soc threat-informed-defense purple-team threat-hunting detection-as-code siem blue-team
cybersecurity telemetry attack-navigator
```

**Settings → General** — enable Issues and Discussions. Upload
`tools/site/og-image.png` as the social preview; without it, links shared on LinkedIn
render as a grey placeholder.

**Settings → Security** — enable Private vulnerability reporting, Dependabot alerts and
Secret scanning. `SECURITY.md` tells people to report privately, so that has to exist.

**Actions** — CI runs automatically on the push. It validates the model, runs the 44
tests, rebuilds every deliverable, checks the tool's JavaScript parses, and fails the
build if authoring-tool traces appear in any shipped file.

## 6. Publish the release

The tag is already pushed. Go to Releases → Draft a new release → choose the existing
`v1.1.0` tag → title `TID-CMM v1.1.0`.

Attach everything from `tid-cmm-release-assets-v1.1.0.zip`:

- `TID-CMM-White-Paper-v1.1.pdf` and `.docx`
- `TID-CMM-Self-Assessment-v1.1.xlsx`
- `TID-CMM-Worked-Example-v1.1.xlsx`
- `tid-cmm-assessment.html` — the offline tool, the most useful attachment
- `tid-cmm-site-upload.zip` — so anyone can self-host
- `model.json`

For the notes, take the v1.1 section of `CHANGELOG.md` and open with the Sysmon figure.

## 7. Rebuilding later

```bash
make all          # validate, test, rebuild everything, provenance check
make provenance   # provenance check on its own
```

`make all` needs Python 3, Node, and LibreOffice for the PDF (`brew install --cask
libreoffice`). Without LibreOffice everything else still builds and the PDF is skipped
with a message.

`build/` is deliberately not committed. It is fully reproducible, and keeping it out
means a stale PDF can never sit beside a current model.
