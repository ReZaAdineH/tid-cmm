"""Build the deployable Cloudflare site and zip it.

    python tools/build_site.py

Produces:
    build/site/                 the deployable tree
    build/tid-cmm-site.zip      drag this into Cloudflare Pages
"""
from __future__ import annotations

import html as html_mod
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tidcmm.model import load_model  # noqa: E402

SRC = ROOT / "tools" / "site"
OUT = ROOT / "build" / "site"
ZIP = ROOT / "build" / "tid-cmm-site.zip"            # everything, for wrangler / git deploys
ZIP_UPLOAD = ROOT / "build" / "tid-cmm-site-upload.zip"  # drag-and-drop bundle
# The dashboard uploader refuses a bundle containing a wrangler config, because it
# assumes the project needs a build step. Ours does not, so these are kept out of
# the drag-and-drop bundle and shipped only in the full one.
UPLOAD_EXCLUDE = {"wrangler.jsonc", "DEPLOY.md"}

NAV = """<div class="topbar"><div class="inner">
  <a class="logo" href="/">TID-CMM<small>Threat-Informed Detection Capability Maturity Model</small><em>Created by Reza Adineh</em></a>
  <nav>
    <a href="/#model">The model</a>
    <a href="/guide">Assessment guide</a>
    <a href="/scoring">Scoring</a>
    <a href="/downloads">Downloads</a>
    <a href="/api">API</a>
    <button class="iconbtn" id="themebtn" onclick="toggleTheme()">&#9790; Dark</button>
    <a href="/assess" class="cta">Start assessment</a>
  </nav>
</div></div>"""


def footer(meta) -> str:
    m = meta["model"]
    return f"""<footer><div class="inner">
  <p><b>TID-CMM</b> v{m['version']} &middot; released {m['released']} &middot;
     <a href="/downloads">Downloads</a> &middot; <a href="/guide">Guide</a> &middot;
     <a href="/scoring">Scoring</a> &middot; <a href="/api">API</a> &middot;
     <a href="{m['repository']}">GitHub</a> &middot; <a href="mailto:{m['contact']}">{m['contact']}</a></p>
  <p>Model content licensed CC-BY-4.0 &middot; code and tooling Apache-2.0 &middot; commercial use permitted with attribution.
     Assessments are self-declared; there is no certification scheme.</p>
  <p>Created and maintained by <b>Reza Adineh</b>.</p>
  <p style="opacity:.7">MITRE ATT&amp;CK&reg; is a registered trademark of The MITRE Corporation. This project is not
     affiliated with or endorsed by MITRE, NIST or SOC-CMM.</p>
</div></footer>"""


def jsonld(*blocks) -> str:
    return "".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>\n'
        for b in blocks if b)


def breadcrumbs(canonical: str, label: str) -> dict | None:
    if not canonical or canonical == "/":
        return None
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://tid-cmm.com/"},
            {"@type": "ListItem", "position": 2, "name": label,
             "item": f"https://tid-cmm.com{canonical}"},
        ],
    }


def faq_block(pairs) -> dict | None:
    """FAQPage markup. Answers are written to stand alone, because that is what a
    featured snippet extracts."""
    if not pairs:
        return None
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs
        ],
    }


def page(title, description, body, meta, *, canonical="", structured=(), label="") -> str:
    url = f"https://tid-cmm.com{canonical}" if canonical else "https://tid-cmm.com/"
    extra = jsonld(breadcrumbs(canonical, label or title.split("—")[0].strip()), *structured)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html_mod.escape(description, quote=True)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TID-CMM">
<meta property="og:title" content="{html_mod.escape(title, quote=True)}">
<meta property="og:description" content="{html_mod.escape(description, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://tid-cmm.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_mod.escape(title, quote=True)}">
<meta name="twitter:description" content="{html_mod.escape(description, quote=True)}">
<meta name="twitter:image" content="https://tid-cmm.com/og-image.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/shared.css">
<script src="/shared.js"></script>
{extra}</head>
<body>
{NAV}
<div class="wrap narrow">
{body}
</div>
{footer(meta)}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# A deliberately small Markdown subset: enough for the two docs pages, with no
# dependency to install on a build machine.
# ---------------------------------------------------------------------------
def md_inline(s: str) -> str:
    s = html_mod.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(md: str) -> str:
    out: list[str] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        # fenced code
        if line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html_mod.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{md_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        # table
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            t = "<table><tr>" + "".join(f"<th>{md_inline(h)}</th>" for h in head) + "</tr>"
            for r in rows:
                t += "<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</table>")
            continue
        # lists
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(md_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(md_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(md_inline(lines[i].lstrip("> ").rstrip()))
                i += 1
            out.append("<blockquote>" + " ".join(buf) + "</blockquote>")
            continue
        # paragraph
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|\||>|```)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>" + md_inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


QUESTIONS = {
    "TI": "Who are we defending against, and how do we know?",
    "TM": "What do their behaviours look like against our architecture?",
    "DC": "Can we see the activity at all?",
    "DE": "Do we build, test and maintain detection like engineers?",
    "AV": "Have we proven any of it works?",
    "AA": "Does detection output become a decision at operational tempo?",
    "IR": "Can we act on what we detect?",
    "GV": "Is this directed, measured and sustainable?",
}

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0b2545"/>
  <path d="M32 10 L52 19 v16 c0 12-8 19-20 23 -12-4-20-11-20-23 V19 Z"
        fill="none" stroke="#63b3d8" stroke-width="4" stroke-linejoin="round"/>
  <circle cx="32" cy="33" r="7" fill="none" stroke="#63b3d8" stroke-width="4"/>
  <circle cx="32" cy="33" r="2.4" fill="#63b3d8"/>
</svg>
"""


def build() -> Path:
    import time
    started = time.time() - 1  # files written from here on belong to this build
    model = load_model()
    meta = model.meta
    m = meta["model"]
    attack = meta["alignment"]["attack"]

    # Some mounted filesystems refuse unlink, so a stale tree can survive rmtree. The
    # zip is therefore built from what this run actually wrote, never from a glob of
    # the directory — otherwise last version's downloads ship alongside this one's.
    if OUT.exists():
        shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "downloads").mkdir(parents=True, exist_ok=True)
    (OUT / "api").mkdir(parents=True, exist_ok=True)

    # ---- static assets -----------------------------------------------------
    shutil.copy(SRC / "shared.css", OUT / "shared.css")
    shutil.copy(SRC / "shared.js", OUT / "shared.js")
    (OUT / "favicon.svg").write_text(FAVICON)
    shutil.copy(SRC / "og-image.png", OUT / "og-image.png")

    # ---- the assessment tool ----------------------------------------------
    tool = (ROOT / "build" / "tid-cmm-assessment.html").read_text()
    # give the tool a link back to the site without touching its self-contained nature
    tool = tool.replace(
        '<button class="iconbtn" onclick="showPage(\'action\')" title="Jump to your action plan">▸ Action plan</button>',
        '<button class="iconbtn" onclick="showPage(\'action\')" title="Jump to your action plan">▸ Action plan</button>\n'
        '    <a class="iconbtn" href="/" style="text-decoration:none" title="Back to tid-cmm.com">↩ Site</a>',
    )
    (OUT / "assess.html").write_text(tool)

    # ---- downloads ---------------------------------------------------------
    # Deliverables are versioned major.minor on disk; the model carries the full semver.
    v = ".".join(m["version"].split(".")[:2])
    downloads = [
        (f"TID-CMM-White-Paper-v{v}.pdf", "White paper (PDF)", "PDF",
         "The full framework: rationale, positioning, all eight domains, method, scoring, worked example and the complete sub-capability register."),
        (f"TID-CMM-White-Paper-v{v}.docx", "White paper (Word)", "DOCX",
         "The same document in editable form, if you want to excerpt it into your own material."),
        (f"TID-CMM-Self-Assessment-v{v}.xlsx", "Self-assessment workbook", "XLSX",
         f"15 tabs: setup, eight domain tabs with full 0–5 descriptors as cell comments, all {attack['techniques']} ATT&CK techniques, dashboard with radar chart, ranked roadmap, crosswalk."),
        (f"TID-CMM-Worked-Example-v{v}.xlsx", "Worked example workbook", "XLSX",
         "A completed assessment, pre-filled, so you can see what the output looks like before you start."),
        ("tid-cmm-assessment.html", "Offline assessment tool", "HTML",
         "The same tool as the online version, as a single file. Works with no network connection at all."),
        ("attack_techniques.csv", "ATT&CK dataset", "CSV",
         f"Normalised ATT&CK Enterprise v{attack['version']}: tactics, platforms, required data components, detection guidance and mitigations per technique."),
        ("model.json", "Machine-readable model", "JSON",
         "The complete model — domains, sub-capabilities, every level descriptor, evidence criteria, profiles and crosswalks."),
        ("attack_actors.csv", "Threat actor technique profiles", "CSV",
         "1,057 ATT&CK groups, campaigns, malware and tools with the techniques each uses — the data behind the threat profiling step."),
        ("attack_detection.csv", "ATT&CK detection strategies", "CSV",
         "Every technique's v19 detection strategies and analytics with the concrete log sources they require."),
        ("telemetry_catalogue.yaml", "Telemetry catalogue", "YAML",
         "How to enable the log sources that carry the bulk of ATT&CK's analytics: channels, tool class and free routes."),
        ("example-report.json", "Example scored report", "JSON",
         "Output of the scoring engine on the worked example, including the constraint log and ranked priorities."),
    ]
    src_map = {
        f"TID-CMM-White-Paper-v{v}.pdf": ROOT / "build" / f"TID-CMM-White-Paper-v{v}.pdf",
        f"TID-CMM-White-Paper-v{v}.docx": ROOT / "build" / f"TID-CMM-White-Paper-v{v}.docx",
        f"TID-CMM-Self-Assessment-v{v}.xlsx": ROOT / "build" / f"TID-CMM-Self-Assessment-v{v}.xlsx",
        f"TID-CMM-Worked-Example-v{v}.xlsx": ROOT / "build" / f"TID-CMM-Worked-Example-v{v}.xlsx",
        "tid-cmm-assessment.html": ROOT / "build" / "tid-cmm-assessment.html",
        "attack_techniques.csv": ROOT / "data" / "attack_techniques.csv",
        "model.json": ROOT / "build" / "model.json",
        "attack_actors.csv": ROOT / "data" / "attack_actors.csv",
        "attack_detection.csv": ROOT / "data" / "attack_detection.csv",
        "telemetry_catalogue.yaml": ROOT / "data" / "telemetry_catalogue.yaml",
        "example-report.json": ROOT / "build" / "example-report.json",
    }
    # The PDF needs LibreOffice, which not every contributor will have. Treat it as
    # optional so the site still builds; everything else is genuinely required.
    optional = {f"TID-CMM-White-Paper-v{v}.pdf"}
    missing = [k for k, p in src_map.items() if not p.exists() and k not in optional]
    if missing:
        raise SystemExit(
            "Missing build artefacts, run `make all` first: " + ", ".join(missing))
    skipped = []
    for name, path in src_map.items():
        if not path.exists():
            skipped.append(name)
            continue
        shutil.copy(path, OUT / "downloads" / name)
    if skipped:
        print(f"  note: {', '.join(skipped)} not built (LibreOffice absent); "
              f"omitted from the downloads page")
    downloads = [d for d in downloads if d[0] not in skipped]

    def size_of(name):
        b = (OUT / "downloads" / name).stat().st_size
        return f"{b/1024/1024:.1f} MB" if b > 1024 * 1024 else f"{b/1024:.0f} KB"

    dl_rows = "\n".join(
        f"""<div class="dl">
      <div class="ico">{kind}</div>
      <div class="txt"><b>{label}</b><span>{html_mod.escape(desc)}</span></div>
      <a class="btn solid small" href="/downloads/{name}" download>Download &middot; {size_of(name)}</a>
    </div>"""
        for name, label, kind, desc in downloads
    )

    # ---- pages -------------------------------------------------------------
    pages_count = 59
    domain_rows = "\n      ".join(
        f"<tr><td><b>{d.id}</b></td><td>{d.name}</td><td>{d.weight}%</td>"
        f"<td>{len(d.subcapabilities)}</td><td>{QUESTIONS[d.id]}</td></tr>"
        for d in model.domains
    )
    index = (SRC / "index.html").read_text()
    for k, val in {
        "{{VERSION}}": m["version"],
        "{{RELEASED}}": m["released"],
        "{{REPO}}": m["repository"],
        "{{CONTACT}}": m["contact"],
        "{{DOMAINS}}": str(len(model.domains)),
        "{{SUBCAPS}}": str(len(model.subcapabilities())),
        "{{ATTACK_VERSION}}": attack["version"],
        "{{TECHNIQUES}}": str(attack["techniques"]),
        "{{PAGES}}": str(pages_count),
        "{{FILEV}}": v,
        "{{DOMAIN_ROWS}}": domain_rows,
    }.items():
        index = index.replace(k, val)
    assert "{{" not in index, "unsubstituted placeholder in index.html"

    org = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "TID-CMM", "url": "https://tid-cmm.com/",
        "logo": "https://tid-cmm.com/og-image.png",
        "description": "An open capability maturity model for threat-informed detection.",
        "sameAs": [m["repository"]],
    }
    website = {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "TID-CMM", "url": "https://tid-cmm.com/",
        "description": ("Threat-Informed Detection Capability Maturity Model — measure whether "
                        "your detection is driven by adversary behaviour and proven to work."),
    }
    app = {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": "TID-CMM Assessment Tool",
        "applicationCategory": "SecurityApplication",
        "operatingSystem": "Any (browser)",
        "url": "https://tid-cmm.com/assess",
        "description": ("Free browser-based detection capability assessment. Derives your in-scope "
                        "MITRE ATT&CK set from your environment, threat actors and attack paths, "
                        "then computes which techniques you cannot detect with the telemetry you "
                        "collect and what to enable."),
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "softwareVersion": m["version"],
        "featureList": [
            "Derived in-scope ATT&CK technique set",
            "Threat actor technique profiling from ATT&CK groups and campaigns",
            "Telemetry assurance and blind-spot analysis",
            "Maturity tiers with entry gates",
            "Prioritised roadmap and 30/60/90 action plan",
            "Runs entirely in the browser with no data transmitted",
        ],
    }
    home_faq = faq_block([
        ("What is a threat-informed detection capability maturity model?",
         "A threat-informed detection capability maturity model measures whether an organisation's "
         "threat detection is driven by the behaviour of the adversaries most likely to attack it, "
         "and whether that detection has been proven to work. TID-CMM scores eight domains and "
         f"{len(model.subcapabilities())} sub-capabilities from 0 to 5, anchored to MITRE ATT&CK "
         f"Enterprise v{attack['version']}."),
        ("Is 100% MITRE ATT&CK coverage a realistic goal?",
         "No. ATT&CK is a catalogue of behaviour observed across all sectors and platforms, not a "
         f"requirements list. Of its {attack['techniques']} techniques, "
         f"{attack['sub_techniques']} are sub-techniques, and the techniques are not comparable "
         "units, so summing them into a percentage is misleading. A realistic goal is deep, "
         "validated coverage of a scoped set derived from your platforms, your prioritised threat "
         "actors and your attack paths — typically 150 to 250 techniques."),
        ("How do I know whether I have the telemetry to detect a technique?",
         "Compare the log sources each technique's ATT&CK detection analytics require against what "
         "you actually collect, weighted by how much of your estate each source covers. TID-CMM "
         "computes this automatically and reports each technique as assured, partial, weak or "
         "blind, then ranks the telemetry to enable by how many in-scope techniques it unblocks."),
        ("How much of MITRE ATT&CK depends on Sysmon?",
         "423 techniques — 89% of all Windows techniques in ATT&CK Enterprise v19.2 — have "
         "detection analytics that reference Sysmon. For 20 of them Sysmon is the only log source "
         "referenced. Organisations without Sysmon or an EDR providing equivalent process, command "
         "line and module telemetry are structurally unable to detect those behaviours."),
        ("Is TID-CMM free?",
         "Yes. The model is licensed CC-BY-4.0 and the tooling Apache-2.0. The assessment tool, "
         "Excel workbook, white paper and datasets are free to download and use commercially with "
         "attribution. There is no account, no certification scheme and nothing to buy."),
    ])
    index = index.replace("</head>", jsonld(org, website, app, home_faq) + "</head>", 1)
    (OUT / "index.html").write_text(index)

    # docs pages
    guide = md_to_html((ROOT / "docs" / "assessment-guide.md").read_text())
    guide_faq = faq_block([
        ("How long does a detection maturity assessment take?",
         "A rapid self-assessment takes half a day with two or three people and gives a directional "
         "baseline. A structured assessment with evidence takes two to three days across six to ten "
         "people. An evidence-based assessment, where artefacts are reviewed against each claimed "
         "level, takes one to two weeks."),
        ("Who should take part in a detection maturity assessment?",
         "At minimum: threat intelligence, security architecture, the detection platform owner, "
         "detection engineering, offensive security or purple team, SOC operations, incident "
         "response, and security leadership for scope and sign-off. An assessment scored by one "
         "person is an opinion rather than an assessment."),
        ("How do I scope which ATT&CK techniques apply to my organisation?",
         "Filter by the platforms you actually run, then by the techniques used by the threat "
         "actors your threat profile ranks, then add anything appearing on a modelled attack path "
         "to a crown jewel. Record every exclusion with a reason. Never scope by ease of "
         "detection."),
    ])
    (OUT / "guide.html").write_text(page(
        "Assessment guide — TID-CMM",
        "How to run a TID-CMM assessment: assessment types, who takes part, scoping the ATT&CK technique set, and the failure modes to avoid.",
        guide + '<p style="margin-top:30px"><a class="btn solid small" href="/assess">Start the assessment &rarr;</a></p>',
        meta, canonical="/guide", label="Assessment guide", structured=(guide_faq,)))

    scoring = md_to_html((ROOT / "docs" / "scoring-reference.md").read_text())
    (OUT / "scoring.html").write_text(page(
        "Scoring reference — TID-CMM",
        "TID-CMM scoring mechanics: weighted rollup, the C1/C2/C3 integrity constraints, maturity bands, the Validated Coverage Score and prioritisation arithmetic.",
        scoring + '<p style="margin-top:30px"><a class="btn solid small" href="/assess">Start the assessment &rarr;</a></p>',
        meta, canonical="/scoring", label="Scoring reference"))

    (OUT / "downloads.html").write_text(page(
        "Downloads — TID-CMM",
        "Download the TID-CMM white paper, Excel self-assessment workbook, worked example, offline assessment tool, ATT&CK dataset and machine-readable model.",
        f"""<h2 style="margin-top:34px">Downloads</h2>
<p class="sub">Everything is free and openly licensed. Model content CC-BY-4.0, code and tooling Apache-2.0.
   No account, no email address, no sales call.</p>
<div class="card">{dl_rows}</div>
<h3>Prefer the source?</h3>
<p>The model, scoring engine, build scripts and tests are on <a href="{m['repository']}">GitHub</a>.
   Everything on this page is generated from that repository by <code>make all</code>.</p>
<p class="note">MITRE ATT&amp;CK content in the dataset is &copy; The MITRE Corporation and used under the ATT&amp;CK Terms of Use.</p>""",
        meta, canonical="/downloads", label="Downloads", structured=(
            {"@context": "https://schema.org", "@type": "Dataset",
             "name": "TID-CMM threat actor technique profiles",
             "description": ("ATT&CK groups, campaigns, malware and tools with the techniques each "
                             "uses, extracted from MITRE ATT&CK Enterprise v" + attack["version"] +
                             ". Groups inherit the techniques of the software they deploy."),
             "url": "https://tid-cmm.com/downloads",
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                               "contentUrl": "https://tid-cmm.com/downloads/attack_actors.csv"}],
             "license": "https://creativecommons.org/licenses/by/4.0/",
             "creator": {"@type": "Organization", "name": "TID-CMM"},
             "keywords": ["MITRE ATT&CK", "threat actors", "threat intelligence",
                          "detection engineering", "TTP mapping"]},
            {"@context": "https://schema.org", "@type": "Dataset",
             "name": "MITRE ATT&CK v" + attack["version"] + " detection strategies and log sources",
             "description": ("Every ATT&CK Enterprise technique with its v19 detection strategies, "
                             "analytics and the concrete log sources and channels those analytics "
                             "require — the data needed to compute detection telemetry coverage."),
             "url": "https://tid-cmm.com/downloads",
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                               "contentUrl": "https://tid-cmm.com/downloads/attack_detection.csv"}],
             "license": "https://creativecommons.org/licenses/by/4.0/",
             "creator": {"@type": "Organization", "name": "TID-CMM"},
             "keywords": ["MITRE ATT&CK", "detection analytics", "log sources", "Sysmon",
                          "telemetry coverage", "SIEM"]},
        )))

    # ---- JSON API ----------------------------------------------------------
    shutil.copy(ROOT / "build" / "model.json", OUT / "api" / "model.json")
    techs = json.loads((ROOT / "build" / "tool_data.json").read_text())["techniques"]
    (OUT / "api" / "techniques.json").write_text(json.dumps(
        {"attack_version": attack["version"], "snapshot_date": attack["snapshot_date"],
         "count": len(techs), "techniques": techs}, ensure_ascii=False))
    (OUT / "api" / "levels.json").write_text(json.dumps(meta["levels"], ensure_ascii=False, indent=2))
    (OUT / "api" / "tiers.json").write_text(json.dumps(meta.get("tiers", []), ensure_ascii=False, indent=2))
    (OUT / "api" / "profiles.json").write_text(json.dumps(
        {"profiles": meta.get("profiles", {}), "detection_classes": meta.get("detection_classes", {}),
         "environment_archetypes": meta.get("environment_archetypes", {})}, ensure_ascii=False, indent=2))
    (OUT / "api" / "constraints.json").write_text(json.dumps(meta["scoring"], ensure_ascii=False, indent=2))

    (OUT / "api" / "index.html").write_text(page(
        "API — TID-CMM",
        "Stable JSON endpoints for the TID-CMM model, ATT&CK technique index, maturity levels and integrity constraints. CORS enabled.",
        f"""<h2 style="margin-top:34px">JSON API</h2>
<p class="sub">Static JSON, served with permissive CORS headers so you can build against the model from anywhere.
   No key, no rate limit, no tracking.</p>
<table>
  <tr><th style="width:230px">Endpoint</th><th>Contents</th></tr>
  <tr><td><code>/api/model.json</code></td><td>The complete model: {len(model.domains)} domains,
      {len(model.subcapabilities())} sub-capabilities, all {len(model.subcapabilities())*6} level descriptors,
      evidence criteria, weights, crosswalks and the scoring rules.</td></tr>
  <tr><td><code>/api/techniques.json</code></td><td>ATT&amp;CK Enterprise v{attack['version']} technique index
      ({len(techs)} techniques) with tactics and platforms, as used by the assessment tool for scoping.</td></tr>
  <tr><td><code>/api/levels.json</code></td><td>The 0&ndash;5 maturity scale with summaries and evidence bars.</td></tr>
  <tr><td><code>/api/constraints.json</code></td><td>Scoring rules, maturity bands and the C1/C2/C3 integrity constraints.</td></tr>
</table>
<h3>Example</h3>
<pre><code>curl -s https://tid-cmm.com/api/model.json \\
  | jq '.domains[] | {{id, name, weight, subcaps: (.subcapabilities|length)}}'

curl -s https://tid-cmm.com/api/model.json \\
  | jq -r '.domains[].subcapabilities[] | [.id, .name, (.crosswalk.nist_csf_2|join(" "))] | @tsv'</code></pre>
<h3>Versioning</h3>
<p>The payload always carries <code>model.version</code>. Breaking changes to the model shape bump the major version
   and are recorded in the <a href="{m['repository']}/blob/main/CHANGELOG.md">changelog</a>. ATT&amp;CK content is
   pinned to the snapshot date in <code>alignment.attack</code>; it is not silently updated underneath you.</p>
<h3>Licence</h3>
<p>Model content CC-BY-4.0 &mdash; use it commercially, including in products, provided attribution is retained.
   ATT&amp;CK content is &copy; The MITRE Corporation under the ATT&amp;CK Terms of Use.</p>""",
        meta, canonical="/api", label="API"))

    # ---- 404 ---------------------------------------------------------------
    (OUT / "404.html").write_text(page(
        "Not found — TID-CMM", "That page does not exist.",
        """<h2 style="margin-top:60px">Not found</h2>
<p class="sub">That page does not exist. It may have moved, or the link may be wrong.</p>
<p><a class="btn solid small" href="/">Home</a> &nbsp;
   <a class="btn solid small" href="/assess">Start the assessment</a> &nbsp;
   <a class="btn solid small" href="/downloads">Downloads</a></p>""",
        meta))

    # ---- Cloudflare configuration -----------------------------------------
    (OUT / "_headers").write_text("""# Cloudflare headers. The site is static, same-origin only,
# and makes no outbound requests — the policy below enforces that rather than trusting it.
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; media-src 'none'; worker-src 'none'; manifest-src 'self'; frame-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: no-referrer
  Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
  X-Permitted-Cross-Domain-Policies: none

# Public datasets are meant to be consumed cross-origin; nothing else is.
/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, OPTIONS
  Cross-Origin-Resource-Policy: cross-origin
  Cache-Control: public, max-age=3600
  X-Content-Type-Options: nosniff

/downloads/*
  Cross-Origin-Resource-Policy: cross-origin
  Cache-Control: public, max-age=86400
  X-Content-Type-Options: nosniff

/shared.css
  Cache-Control: public, max-age=86400
/shared.js
  Cache-Control: public, max-age=86400
/og-image.png
  Cache-Control: public, max-age=604800
""")

    # A published contact route for anyone who finds a flaw. Costs nothing and is the
    # difference between a quiet disclosure and a public one.
    (OUT / ".well-known").mkdir(exist_ok=True)
    (OUT / ".well-known" / "security.txt").write_text(f"""Contact: mailto:{m['contact']}
Expires: 2027-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: https://tid-cmm.com/.well-known/security.txt
Policy: https://tid-cmm.com/about

# TID-CMM is a static site. It stores nothing server-side, sets no cookies, runs no
# analytics and makes no outbound requests. Assessment data stays in the visitor's
# browser. If you have found a way to make that untrue, please tell us.
""")

    (OUT / "_redirects").write_text("""# Cloudflare Pages redirects
/assessment          /assess              301
/self-assessment     /assess              301
/tool                /assess              301
/whitepaper          /downloads           301
/white-paper         /downloads           301
/the-framework       /#model              301
/why-tdmm            /                    301
/get-started         /assess              301
/open-collaboration  /downloads           301
/threat-detection-maturity-model-tdmm  /  301
/who-its-for         /                    301
/model.json          /api/model.json      301
""")

    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://tid-cmm.com/sitemap.xml\n")

    urls = ["/", "/assess", "/guide", "/scoring", "/downloads", "/api"]
    from datetime import date
    today = date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>https://tid-cmm.com{u}</loc>"
                  f"<lastmod>{today}</lastmod>"
                  f"<priority>{'1.0' if u in ('/', '/assess') else '0.7'}</priority></url>\n" for u in urls)
        + "</urlset>\n")

    # Workers static-assets config, for the alternative deploy path
    (OUT / "wrangler.jsonc").write_text("""{
  // Deploy with Cloudflare Workers instead of Pages:
  //   npx wrangler deploy
  // Pages direct upload does not use this file and will ignore it.
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "tid-cmm",
  "compatibility_date": "2026-08-01",
  "assets": {
    "directory": "./",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
""")

    (OUT / "DEPLOY.md").write_text(f"""# Deploying this site to Cloudflare

The site is entirely static. There is no build step, no framework, no dependencies and no server-side code.
Every page works from `file://` too, except the root-relative links.

## Option A — Cloudflare Pages, direct upload (fastest)

1. Cloudflare dashboard &rarr; **Workers & Pages** &rarr; **Create** &rarr; **Pages** &rarr; **Upload assets**.
2. Name the project `tid-cmm`.
3. Drag in **`tid-cmm-site.zip`** (or the unzipped folder). Do not nest it inside another folder — `index.html`
   must be at the root of what you upload.
4. **Deploy.** You get `https://tid-cmm.pages.dev` immediately.

### Attaching tid-cmm.com

1. Project &rarr; **Custom domains** &rarr; **Set up a custom domain** &rarr; `tid-cmm.com`.
2. Repeat for `www.tid-cmm.com` if you want it.
3. If the domain is already on Cloudflare, DNS is written for you. If it is elsewhere, Cloudflare shows the
   CNAME to add.
4. The site is currently on WordPress.com — point the domain at Cloudflare only when you are ready to cut over,
   because DNS will move the live site.

`_redirects` already maps the old WordPress URLs (`/the-framework`, `/why-tdmm`, `/get-started`,
`/open-collaboration`, `/who-its-for`, `/threat-detection-maturity-model-tdmm`) so existing links and any
search-engine results keep working.

## Option B — Cloudflare Workers

```bash
cd site
npx wrangler deploy
```

`wrangler.jsonc` is included and configured for static assets with `404.html` handling.

## Option C — Git-connected Pages

Commit the contents of this folder to a repository, then Workers & Pages &rarr; Create &rarr; Pages &rarr;
Connect to Git. Framework preset: **None**. Build command: leave empty. Build output directory: `/`.

## What is in here

```
index.html          Landing page
assess.html         The assessment tool (self-contained, ~290 KB)
guide.html          Assessment guide
scoring.html        Scoring reference
downloads.html      Download index
404.html            Not-found page
api/                model.json, techniques.json, levels.json, constraints.json (CORS enabled)
downloads/          White paper (PDF + DOCX), both workbooks, offline tool, ATT&CK CSV, JSON
shared.css          Site styles
shared.js           Theme persistence and nav highlighting
favicon.svg
_headers            Security headers and cache policy
_redirects          Legacy WordPress URL mapping
sitemap.xml
robots.txt
wrangler.jsonc      Only needed for the Workers deploy path
```

## Privacy

The site makes **no external requests**. No fonts, no CDN, no analytics, no trackers. The Content-Security-Policy
in `_headers` sets `connect-src 'none'`, which means the browser will block any network call the page tries to
make — an enforced guarantee that assessment data cannot leave the user's machine.

The assessment tool stores progress in `localStorage` on the visitor's own device, and degrades gracefully if
storage is unavailable (private browsing). Nothing is transmitted; there is no server to transmit it to.

## Regenerating

From the repository root:

```bash
make all                      # rebuild the model, workbook, tool and white paper
python tools/build_site.py    # rebuild this site and the zip
```

TID-CMM v{m['version']} &middot; {m['released']}
""")

    # ---- zip ---------------------------------------------------------------
    # Truncate in place rather than unlink: some mounted filesystems disallow unlink.
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.stat().st_mtime >= started)
    stale = sorted(p.relative_to(OUT) for p in OUT.rglob("*")
                   if p.is_file() and p.stat().st_mtime < started)
    if stale:
        print(f"  note: {len(stale)} stale file(s) left in {OUT.name}/ from a previous build "
              f"were excluded from the zips: {', '.join(str(x) for x in stale[:4])}"
              + (" ..." if len(stale) > 4 else ""))
    for target, exclude in ((ZIP, set()), (ZIP_UPLOAD, UPLOAD_EXCLUDE)):
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for p in files:
                rel = p.relative_to(OUT)
                if str(rel) in exclude:
                    continue
                z.write(p, rel)
    return ZIP_UPLOAD


if __name__ == "__main__":
    build()
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    n = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"{OUT}  ({n} files, {total/1024/1024:.1f} MB)")
    with zipfile.ZipFile(ZIP_UPLOAD) as z:
        print(f"{ZIP_UPLOAD}  ({len(z.namelist())} files, {ZIP_UPLOAD.stat().st_size/1024/1024:.1f} MB)  <- drag this in")
    with zipfile.ZipFile(ZIP) as z:
        print(f"{ZIP}  ({len(z.namelist())} files, {ZIP.stat().st_size/1024/1024:.1f} MB)  <- wrangler / git")
