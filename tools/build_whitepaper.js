/**
 * Build the TID-CMM white paper (.docx).
 *
 *   node tools/build_whitepaper.js build/TID-CMM-White-Paper-v1.0.docx
 *
 * Appendices are generated from build/model.json so the paper cannot drift
 * from the machine-readable model.
 */
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, TableOfContents,
  Header, Footer, PageNumber, LevelFormat, convertInchesToTwip, PositionalTab,
  PositionalTabAlignment, PositionalTabLeader,
} = D;

const ROOT = path.resolve(__dirname, "..");
const MODEL = JSON.parse(fs.readFileSync(path.join(ROOT, "build", "model.json"), "utf8"));
const REPORT = JSON.parse(fs.readFileSync(path.join(ROOT, "build", "example-report.json"), "utf8"));

const NAVY = "0B2545", ACCENT = "0B4F6C", INK = "1F2933", MUTED = "5B6B78", RULE = "C9D6DE";
const FONT = "Calibri";
const PAGE_W = 9026; // usable width in DXA for A4 with 1" margins

/* ------------------------------------------------------------- helpers */
const P = (text, o = {}) => new Paragraph({
  spacing: { before: o.before ?? 0, after: o.after ?? 140, line: o.line ?? 276 },
  alignment: o.align,
  indent: o.indent,
  border: o.border,
  shading: o.shading,
  keepNext: o.keepNext,
  children: Array.isArray(text) ? text : [new TextRun({
    text, font: FONT, size: o.size ?? 21, color: o.color ?? INK,
    bold: o.bold, italics: o.italics,
  })],
});

const R = (text, o = {}) => new TextRun({
  text, font: FONT, size: o.size ?? 21, color: o.color ?? INK,
  bold: o.bold, italics: o.italics, break: o.break,
});

const H = (text, level, o = {}) => new Paragraph({
  heading: level,
  pageBreakBefore: o.pageBreak,
  spacing: { before: o.before ?? 260, after: o.after ?? 120 },
  children: [new TextRun({
    text, font: FONT, bold: true,
    size: level === HeadingLevel.HEADING_1 ? 30 : level === HeadingLevel.HEADING_2 ? 25 : 22,
    color: level === HeadingLevel.HEADING_1 ? NAVY : ACCENT,
  })],
});
const H1 = (t, o) => H(t, HeadingLevel.HEADING_1, o);
const H2 = (t, o) => H(t, HeadingLevel.HEADING_2, o);
const H3 = (t, o) => H(t, HeadingLevel.HEADING_3, o);

const BULLET = (text, o = {}) => new Paragraph({
  numbering: { reference: "bullets", level: o.level ?? 0 },
  spacing: { after: 70, line: 264 },
  children: Array.isArray(text) ? text : [R(text, o)],
});
const NUM = (text, o = {}) => new Paragraph({
  numbering: { reference: "numbers", level: 0 },
  spacing: { after: 70, line: 264 },
  children: Array.isArray(text) ? text : [R(text, o)],
});

const CALLOUT = (title, body) => new Paragraph({
  spacing: { before: 140, after: 180, line: 268 },
  shading: { type: ShadingType.CLEAR, fill: "EEF4F7" },
  border: {
    left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 8 },
    top: { style: BorderStyle.SINGLE, size: 2, color: "EEF4F7", space: 6 },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: "EEF4F7", space: 6 },
    right: { style: BorderStyle.SINGLE, size: 2, color: "EEF4F7", space: 6 },
  },
  children: [R(title + " ", { bold: true, color: NAVY }), R(body)],
});

function cell(text, o = {}) {
  return new TableCell({
    width: { size: o.width, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    verticalAlign: D.VerticalAlign.CENTER,
    columnSpan: o.span,
    children: (Array.isArray(text) ? text : [text]).map(t =>
      typeof t === "string"
        ? new Paragraph({
            spacing: { after: 0, line: 250 },
            alignment: o.align,
            children: [R(t, { size: o.size ?? 18, bold: o.bold, color: o.color ?? INK })],
          })
        : t),
  });
}

function table(headers, rows, widths, opts = {}) {
  const trs = [];
  if (headers) {
    trs.push(new TableRow({
      tableHeader: true,
      children: headers.map((h, i) => cell(h, { width: widths[i], fill: NAVY, bold: true, color: "FFFFFF", size: opts.size ?? 18 })),
    }));
  }
  rows.forEach((r, ri) => {
    trs.push(new TableRow({
      children: r.map((c, i) => cell(c, {
        width: widths[i],
        fill: opts.zebra !== false && ri % 2 === 1 ? "F4F8FA" : undefined,
        size: opts.size ?? 18,
        bold: opts.boldFirstCol && i === 0,
      })),
    }));
  });
  return new Table({
    columnWidths: widths,
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      left: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      right: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    },
    rows: trs,
  });
}

const SPACER = (h = 100) => new Paragraph({ spacing: { after: h }, children: [] });
const CAPTION = (t) => P(t, { size: 17, italics: true, color: MUTED, after: 200 });

/* --------------------------------------------------------------- content */
const attack = MODEL.alignment.attack;
const nSub = MODEL.domains.reduce((a, d) => a + d.subcapabilities.length, 0);

const body = [];

/* ---- cover ---- */
body.push(
  SPACER(1600),
  P([R("TID-CMM", { size: 66, bold: true, color: NAVY })], { after: 60 }),
  P([R("Threat-Informed Detection Capability Maturity Model", { size: 32, color: ACCENT })], { after: 240 }),
  new Paragraph({
    spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: ACCENT, space: 6 } },
    children: [],
  }),
  P([R("A framework for measuring whether your detection capability is driven by adversary behaviour — and whether it has been proven to work.", { size: 24, color: INK })], { after: 400 }),
  P([R(`Version ${MODEL.model.version}`, { bold: true }), R(`   ·   Released ${MODEL.model.released}`)], { after: 60 }),
  P([R(`Aligned to MITRE ATT&CK Enterprise v${attack.version} (${attack.techniques} techniques, ${attack.data_components} data components)`, { color: MUTED, size: 19 })], { after: 40 }),
  P([R("Crosswalked to NIST CSF 2.0, SOC-CMM, ISO/IEC 27001:2022 and MITRE D3FEND", { color: MUTED, size: 19 })], { after: 40 }),
  P([R(`${MODEL.domains.length} domains  ·  ${nSub} sub-capabilities  ·  ${nSub * 6} level descriptors`, { color: MUTED, size: 19 })], { after: 500 }),
  P([R(MODEL.model.homepage, { color: ACCENT }), R("   ·   "), R(MODEL.model.contact, { color: ACCENT })], { after: 40 }),
  P([R(`Licence: ${MODEL.model.licence}`, { color: MUTED, size: 18 })]),
  new Paragraph({ children: [new PageBreak()] }),
);

/* ---- contents ---- */
const CONTENTS = [
  ["Executive summary", []],
  ["1. Why detection programmes plateau", ["1.1 The measurement problem", "1.2 The three failure modes", "1.3 What the plateau looks like"]],
  ["2. What already exists, and what is missing", ["2.1 The gap, stated precisely"]],
  ["3. Design principles", ["3.1 Evidence over assertion", "3.2 Behaviour over inventory", "3.3 Whole loop, not one function", "3.4 Constraints over exhortation", "3.5 Scope honestly, then measure", "3.6 Two audiences, one assessment"]],
  ["4. The model", ["4.1 Structure", "4.2 The maturity scale", "4.3 The three integrity constraints", "4.4 The Validated Coverage Score"]],
  ["5. The domains in detail", MODEL.domains.map((d, i) => `5.${i + 1} ${d.id} — ${d.name}`)],
  ["6. Running an assessment", ["6.1 Choose the assessment type", "6.2 Who takes part", "6.3 Sequence", "6.4 Common failure modes in the assessment itself"]],
  ["7. Scoring mechanics", ["7.1 Rollup", "7.2 Order of operations", "7.3 Bands", "7.4 Prioritisation arithmetic"]],
  ["8. The toolkit", ["8.1 Privacy", "8.2 Consistency between implementations"]],
  ["9. Worked example", ["9.1 Scope", "9.2 Results", "9.3 Coverage", "9.4 The roadmap", "9.5 What the CISO is told"]],
  ["10. Adoption", ["10.1 A first ninety days", "10.2 Setting a target", "10.3 Re-assessment", "10.4 Contributing", "10.5 Licence"]],
  ["Appendix A — Full sub-capability register", []],
  ["Appendix B — Framework crosswalk", []],
  ["Appendix C — ATT&CK alignment and scoping", []],
  ["Appendix D — Glossary", []],
];
body.push(H1("Contents"));
CONTENTS.forEach(([chapter, sections]) => {
  body.push(P([R(chapter, { bold: true, color: NAVY, size: 22 })], { before: 120, after: 40 }));
  sections.forEach(s => body.push(P([R(s, { color: MUTED, size: 19 })],
    { after: 20, indent: { left: convertInchesToTwip(0.28) } })));
});
body.push(new Paragraph({ children: [new PageBreak()] }));

/* ---- executive summary ---- */
body.push(
  H1("Executive summary"),
  P("Most organisations cannot answer a simple question about their own security operations: against the adversaries most likely to attack us, what proportion of their behaviour would we actually see — and how do we know?"),
  P("The question is harder than it sounds, and the reason is structural. Detection capability is usually described by the things that are easy to count: the number of log sources onboarded, the number of rules enabled, the number of alerts triaged, the number of techniques shaded green on an ATT&CK Navigator layer. None of these measures capability. A rule that has never fired on a true positive, running on a log source that stopped reporting six weeks ago, mapped to a technique the organisation's adversaries do not use, counts identically to a rule that has been proven by emulation to catch a real intrusion within minutes."),
  P("TID-CMM exists to close that gap. It is a maturity model in the conventional sense — eight domains, fifty-three sub-capabilities, each scored from 0 to 5 with explicit descriptors — but it differs from its peers in three deliberate ways."),
  SPACER(60),
  BULLET([R("It treats adversarial validation as a first-class domain, not an afterthought. ", { bold: true }), R("Atomic testing, breach and attack simulation, threat-actor emulation, purple teaming, penetration testing and red teaming are scored together as the evidence engine of the whole model.")]),
  BULLET([R("It treats threat modeling and attack path analysis as a first-class domain. ", { bold: true }), R("Threat intelligence tells you what an adversary does in general; attack trees and computed attack paths tell you what that behaviour looks like against your architecture, your identities and your crown jewels. Without that step, ATT&CK coverage is a generic checklist.")]),
  BULLET([R("It refuses to let the assessment flatter itself. ", { bold: true }), R("Three integrity constraints are applied mechanically at scoring time: no domain may exceed the validation domain by more than one level; detection engineering may not exceed the telemetry it runs on by more than one level; and a score of 4 or 5 without a named artefact is counted as a 3.")]),
  SPACER(80),
  P("Those constraints are the model's distinguishing feature, and they are not decorative. In the worked example in Chapter 9, an organisation with genuinely strong security operations self-assesses at 2.44. After the constraints are applied it scores 2.34, and the reason is visible in one line of output: four separate domains were capped because the organisation had never emulated an adversary against the capability it was claiming. The model does not merely report a lower number; it identifies the single investment that would raise every other domain."),
  CALLOUT("The central claim.", "An untested detection capability is an assumed detection capability. A maturity model that scores assumptions the same way it scores evidence will systematically overstate readiness, and will do so most severely in the organisations that have spent the most money."),
  P("TID-CMM is open. The model is published as machine-readable YAML with a JSON schema, a Python scoring engine, an Excel self-assessment workbook and a single-file browser tool that requires no installation and transmits nothing. Model content is licensed CC-BY-4.0 and the tooling Apache-2.0, so organisations can embed it in internal assurance processes and vendors can implement it without negotiation."),
  P("The intended outcome of an assessment is not a number. It is a ranked list of the things that would most improve your ability to see an adversary, expressed in terms your detection engineers can act on and your board can fund."),
);

/* ---- ch 1 ---- */
body.push(
  H1("1. Why detection programmes plateau", { pageBreak: true }),
  H2("1.1 The measurement problem"),
  P("A security operations function that has been running for five years will typically have accumulated a large detection estate: several thousand rules across a SIEM, an EDR platform, an identity provider, a cloud-native detection service and whatever the email gateway contributes. It will have onboarded most of the log sources anyone thought to ask for. It will have an incident response plan, a case management platform, a threat intelligence subscription and a set of dashboards."),
  P("It will also, usually, be unable to say which of those rules work."),
  P("This is not incompetence. It is the predictable result of measuring the wrong things for a long time. Consider what the standard metrics actually tell you:"),
  SPACER(60),
  table(
    ["Common metric", "What it appears to measure", "What it actually measures"],
    [
      ["Number of detection rules", "Detection breadth", "Historical accumulation, including duplicates, vendor defaults and content nobody dares disable"],
      ["ATT&CK techniques ‘covered’", "Adversary coverage", "How many rules have had a technique ID typed into a metadata field"],
      ["Alerts triaged per analyst", "Operational throughput", "Noise volume, which usually correlates negatively with precision"],
      ["Mean time to detect", "Speed of detection", "Speed of detecting the things you already detect. It is silent on everything you miss"],
      ["Log sources onboarded", "Visibility", "Ingestion, not coverage. It says nothing about parsing, completeness, timeliness or whether anything queries the data"],
      ["Threats blocked", "Protection", "Perimeter noise. It is dominated by commodity scanning and tells you nothing about targeted intrusion"],
    ],
    [2400, 3000, 3626],
  ),
  CAPTION("Table 1.1 — Standard security operations metrics and what they are actually measuring."),
  P("Each metric has a common property: it can be improved without improving the organisation's ability to detect an adversary, and in several cases it improves fastest when capability degrades. Alert volume rises when tuning is neglected. Rule count rises when nothing is retired. Mean time to detect improves when the noisy, easy, low-value detections dominate the sample."),
  H2("1.2 The three failure modes"),
  P("Across detection programmes, the same three failures recur, and they are the failures the model is built to expose."),
  H3("Failure one: coverage claimed without visibility"),
  P("A detection rule is written against a data source that is only deployed on 60% of the estate, or that stopped parsing correctly after a vendor agent upgrade, or whose ingestion pipeline silently drops events above a volume threshold. The rule exists. It is enabled. It is mapped to a technique. It cannot fire. Nobody knows, because nothing tests it and nothing monitors the dependency."),
  P("This failure is invisible to every metric in Table 1.1. It is why TID-CMM makes telemetry quality a scored sub-capability with its own ceiling rule, and why detection engineering cannot score more than one level above the telemetry domain."),
  H3("Failure two: detection built without a threat model"),
  P("An organisation buys a detection content subscription and enables everything. Coverage of the ATT&CK matrix rises impressively. But the content was written for a generic enterprise, and the organisation's actual exposure — a bespoke payment application, a specific cloud entitlement path to the customer database, a third-party integration with standing privileged access — is not in the matrix in any actionable form. The adversary who matters does not need to use a technique the content covers. They need to use the path nobody modelled."),
  P("Generic ATT&CK coverage is a necessary foundation and an insufficient one. TID-CMM addresses this by scoring attack tree construction and attack path analysis as distinct capabilities, and by requiring traceability from a modelled node to a deployed detection to a validation result."),
  H3("Failure three: capability asserted without evidence"),
  P("The most consequential failure. Someone is asked whether the organisation would detect credential dumping. They think about it, recall that there is a rule for it, and say yes. That answer then propagates into a risk register, a board report, a regulatory submission and a budget decision. It is never tested. When it is tested — usually by an adversary — the answer turns out to be no, for a reason that would have taken twenty minutes of emulation to discover."),
  CALLOUT("Why this failure dominates.", "Assertion is free and testing is not. In any assessment process where an unevidenced claim scores the same as an evidenced one, assertion will drive out evidence, because the incentives are unambiguous. The only durable fix is structural: make the unevidenced claim score lower."),
  H2("1.3 What the plateau looks like"),
  P("The observable symptom is a programme that spends steadily and improves little. Tooling is refreshed, headcount grows modestly, dashboards proliferate, and yet the same categories of intrusion succeed in the same way. Post-incident reviews produce lessons that are identified but not engineered. Penetration test reports are read by the risk function and never reach the detection engineers. Purple team exercises happen once, produce a long finding list, and the findings age quietly in a tracker."),
  P("The plateau is not a resourcing problem. It is a feedback problem. The loop that should connect intelligence to modelling to telemetry to detection to validation to improvement is broken in several places at once, and no single team can see the whole break. A maturity model is useful here precisely because it forces the whole loop into one picture."),
);

/* ---- ch 2 ---- */
body.push(
  H1("2. What already exists, and what is missing", { pageBreak: true }),
  P("TID-CMM is not built in a vacuum, and it deliberately does not duplicate work that is already good. This chapter states what each adjacent framework does well, and the specific gap that justifies another model."),
  SPACER(60),
  table(
    ["Framework", "What it does well", "Where it leaves a gap for TID-CMM"],
    [
      ["MITRE ATT&CK", "A shared, evidenced vocabulary for adversary behaviour, maintained and versioned. The single most valuable contribution to defensive practice in a decade.", "It is a knowledge base, not a maturity model. It describes behaviour; it does not tell you whether your organisation's process for turning that behaviour into detection is any good, nor whether your claimed coverage is real."],
      ["SOC-CMM", "Rigorous, well-established assessment of the SOC as an organisational function across business, people, process, technology and services. Excellent for structuring a security operations capability.", "It assesses the SOC as an operating unit. It is comparatively light on technique-level detection coverage, on adversarial validation as a discipline, and on attack path analysis. It answers ‘is this a well-run SOC?’ more than ‘would this SOC see the adversary?’"],
      ["NIST CSF 2.0", "The common language for expressing cybersecurity posture to executives, regulators and insurers. Broad, governance-aware, and now with a Govern function that materially improves it.", "Deliberately outcome-level and technology-neutral. ‘DE.CM-09: computing hardware and software are monitored to find potentially adverse events’ is correct and unarguable, and provides no way to distinguish a programme that does this well from one that does it nominally."],
      ["Elastic DEBMM", "A focused, practical model for detection engineering behaviour specifically, and a genuine advance in treating detection as an engineering discipline.", "Scoped, by design, to detection engineering. It does not extend to threat modeling, attack path analysis, adversarial validation, response or governance, and so cannot produce a whole-loop picture."],
      ["Hunting Maturity Model", "A clear, widely understood scale for hunting capability that has usefully shaped practice.", "Single-capability scope. Hunting is one sub-capability within one domain of a detection programme."],
      ["Gartner CTEM", "The right cycle for exposure management — scoping, discovery, prioritisation, validation, mobilisation — and it correctly elevates validation.", "Exposure-centric rather than detection-centric. It asks whether an exposure can be exploited; TID-CMM asks whether the exploitation would be seen. The two are complementary and TID-CMM's attack path sub-capability is explicitly crosswalked to CTEM."],
      ["ISO/IEC 27001:2022", "Auditable management-system discipline and international recognition.", "Control-existence oriented. An organisation can be certified while detecting almost nothing, because the standard asks whether a control is implemented and reviewed, not whether it works against an adversary."],
      ["C2M2, CMMC and sector models", "Strong domain structure and, in CMMC's case, assessed rather than self-declared.", "Compliance-anchored and slow-moving relative to adversary tradecraft. Neither is designed to be re-run quarterly against a shifting threat profile."],
    ],
    [1500, 3400, 4126],
  ),
  CAPTION("Table 2.1 — Adjacent frameworks and the gap TID-CMM addresses."),
  H2("2.1 The gap, stated precisely"),
  P("There is no widely adopted, open model that does all four of the following at once:"),
  NUM("Scores the complete loop from intelligence, through threat modeling and attack path analysis, through telemetry and detection engineering, through adversarial validation, to response and governance."),
  NUM("Anchors coverage claims to ATT&CK at technique and sub-technique level, while explicitly rejecting whole-matrix coverage as a vanity metric."),
  NUM("Requires adversarial validation as the evidence for capability claims, and structurally prevents a high score without it."),
  NUM("Is machine-readable, freely licensed, and shipped with working tooling rather than a PDF and an invitation to build your own spreadsheet."),
  P("TID-CMM is designed to occupy that space, and to sit alongside rather than replace the frameworks above. An organisation running SOC-CMM should keep running it; the crosswalk in Appendix B lets a TID-CMM assessment feed the same reporting. An organisation reporting in NIST CSF 2.0 terms can map every sub-capability to a CSF outcome and use TID-CMM as the evidence layer underneath."),
);

/* ---- ch 3 ---- */
body.push(
  H1("3. Design principles", { pageBreak: true }),
  P("Six principles governed the design, and each one has a visible consequence in the model."),
  H2("3.1 Evidence over assertion"),
  P("Every sub-capability defines what evidence would justify each level, and the scoring engine enforces it at the top of the scale. In strict mode, a 4 or a 5 without a named artefact is recorded as a 3, with the reason logged. This is not an accusation of dishonesty; it is a recognition that self-assessment without an evidence rule reliably drifts upward, and that the drift is largest in exactly the areas where nobody has looked."),
  H2("3.2 Behaviour over inventory"),
  P("The model scores what the organisation does, not what it owns. No sub-capability asks whether a particular class of product has been purchased. Several ask whether the outcome that product is meant to deliver has been achieved and demonstrated. An organisation can reach Level 4 in analytics and automation with modest tooling and excellent process; it cannot reach it with excellent tooling and no process."),
  H2("3.3 Whole loop, not one function"),
  P("Detection capability is a loop, and loops fail at their weakest joint. Scoring detection engineering in isolation produces a locally optimised function attached to broken inputs and outputs. The eight domains cover the full circuit, and the weighting reflects that detection engineering is the largest single contributor but nowhere near a majority."),
  H2("3.4 Constraints over exhortation"),
  P("Most maturity models handle the risk of over-scoring by telling assessors to be honest. TID-CMM handles it arithmetically. If the validation domain scores 1.6, every other domain is capped at 2.6 regardless of what the assessor believes, and the cap is reported explicitly rather than hidden in the total. Exhortation does not survive a budget cycle; arithmetic does."),
  H2("3.5 Scope honestly, then measure"),
  P("The model rejects coverage measured against the full ATT&CK matrix. An organisation with no macOS estate and no container platform gains nothing from reporting that it does not detect techniques it cannot experience. It must instead define an in-scope technique set from its platforms and its prioritised threat profile, record the rationale, and measure against that. This makes the number smaller, more difficult to game and considerably more useful."),
  CALLOUT("A warning that is built into the tooling.", "A high coverage score over a small, conveniently chosen in-scope set is worse than a low score over an honest one, because it is persuasive. Both the workbook and the browser tool display the in-scope count beside the score for exactly this reason."),
  H2("3.6 Two audiences, one assessment"),
  P("A detection engineer needs technique-level gaps, data component dependencies and the specific descriptor of the next level up. A CISO needs a defensible statement of what the organisation can and cannot detect, what that costs, and what changes if it is funded. These are different reports from the same data, and the tooling produces both without a second assessment."),
);

/* ---- ch 4: the model ---- */
body.push(
  H1("4. The model", { pageBreak: true }),
  H2("4.1 Structure"),
  P(`TID-CMM v${MODEL.model.version} comprises ${MODEL.domains.length} domains and ${nSub} sub-capabilities. Each sub-capability is scored 0 to 5 against explicit descriptors, or marked not applicable with a recorded rationale. Sub-capability scores roll up to a weighted domain score; domain scores roll up to a weighted overall score.`),
  SPACER(60),
  table(
    ["Domain", "Name", "Weight", "Sub-capabilities", "Question it answers"],
    MODEL.domains.map(d => [
      d.id, d.name, d.weight + "%", String(d.subcapabilities.length),
      {
        TI: "Who are we defending against, and how do we know?",
        TM: "What do their behaviours look like against our architecture?",
        DC: "Can we see the activity at all?",
        DE: "Do we build, test and maintain detection like engineers?",
        AV: "Have we proven any of it works?",
        AA: "Does detection output become a decision at operational tempo?",
        IR: "Can we act on what we detect?",
        GV: "Is this directed, measured and sustainable?",
      }[d.id],
    ]),
    [800, 2700, 800, 1100, 3626],
    { boldFirstCol: true },
  ),
  CAPTION("Table 4.1 — The eight domains, their weights and the question each answers."),
  P("The weighting is a judgement, and it is exposed as an editable parameter in every tool so an organisation can defend a different one. Detection engineering carries the largest weight (16%) because it is where capability is manufactured. Telemetry and adversarial validation follow at 14% each because they are, respectively, the precondition and the proof. Governance and incident response carry 10% each — not because they matter less, but because both are extensively covered by other frameworks the organisation is likely already running, and TID-CMM's marginal contribution there is smaller."),
  H2("4.2 The maturity scale"),
  P("The same six-point scale applies to every sub-capability. The scale is deliberately not the classic CMMI wording; the third level is named Threat-Informed rather than Defined, because in this model the step from 2 to 3 is precisely the step from doing something consistently to doing it because a specific adversary made it necessary."),
  SPACER(60),
  table(
    ["Level", "Name", "What it means", "Evidence bar"],
    MODEL.levels.map(l => [String(l.value), l.name, l.summary, l.evidence_bar]),
    [700, 1500, 4400, 2426],
    { boldFirstCol: true },
  ),
  CAPTION("Table 4.2 — The TID-CMM maturity scale."),
  P("Two properties of the scale deserve comment. First, the step from 3 to 4 is the largest in the model, because it is the step from doing threat-informed work to proving it. Most organisations that consider themselves mature sit between 2.5 and 3.5; the population above 4 is small and, in the authors' experience, always contains a substantial validation programme. Second, Level 5 requires contribution back to the community. This is a deliberate statement about what an optimising security function looks like: it is one whose learning does not stop at its own perimeter."),
  H2("4.3 The three integrity constraints"),
  P("These are the mechanism that distinguishes TID-CMM from a self-assessment questionnaire. They are applied by the scoring engine after the raw scores are collected, and every adjustment is reported."),
  SPACER(60),
  ...MODEL.scoring.constraints.flatMap(c => [
    H3(`${c.id} — ${c.name}`),
    P(c.rule),
  ]),
  P("Constraint C1 encodes the model's central claim: an untested capability is an assumed capability. It permits a one-level margin, which acknowledges that a capability can be genuinely well-built before it has been validated — but only just. Constraint C2 encodes the physical reality that detection logic cannot outperform its inputs. Constraint C3 makes evidence the price of a high score."),
  P("These constraints are visible, not hidden. Every tool reports the unadjusted self-assessed score beside the adjusted one, together with a line stating which constraint was applied and why. The gap between the two numbers is itself a finding, and often the most useful one in the assessment."),
  H2("4.4 The Validated Coverage Score"),
  P("Alongside the maturity score, TID-CMM defines a coverage metric that is deliberately harder to game than a Navigator layer. Each in-scope ATT&CK technique is scored on a four-point scale:"),
  SPACER(60),
  table(
    ["Status", "Meaning", "What it requires"],
    [
      ["0", "No telemetry", "The activity would generate no record you collect. You are blind."],
      ["1", "Telemetry only", "The data exists and is queryable. Nothing alerts. Useful for hunting and investigation, not for detection."],
      ["2", "Detection logic exists", "A rule or analytic is deployed and healthy. It has not been proven to fire on the real behaviour."],
      ["3", "Validated by emulation", "The behaviour has been executed and the detection observed to fire, within the defined recency window."],
    ],
    [900, 2300, 5826],
    { boldFirstCol: true },
  ),
  CAPTION("Table 4.3 — The coverage status scale underlying the Validated Coverage Score."),
  P("The Validated Coverage Score is the achieved points divided by the maximum available across the in-scope set, expressed as a percentage. It is reported alongside the domain scores, never instead of them, and always beside the in-scope technique count."),
  CALLOUT("Recency matters.", "A status of 3 expires. A validation result older than the organisation's defined review window is downgraded to 2, because a detection proven to work eighteen months ago, across two platform migrations and a data model change, is not proven to work now."),
);

/* ---- ch 5: domains ---- */
body.push(H1("5. The domains in detail", { pageBreak: true }));
MODEL.domains.forEach((d, i) => {
  body.push(
    H2(`5.${i + 1}  ${d.id} — ${d.name}`, { pageBreak: i > 0 }),
    P([R("Weight ", { bold: true, color: MUTED, size: 19 }), R(`${d.weight}%`, { size: 19, color: MUTED }),
       R("   ·   ", { size: 19, color: MUTED }),
       R(`${d.subcapabilities.length} sub-capabilities`, { size: 19, color: MUTED })], { after: 100 }),
    P(d.intent),
  );
  if (d.anti_pattern) {
    body.push(new Paragraph({
      spacing: { before: 100, after: 180, line: 268 },
      shading: { type: ShadingType.CLEAR, fill: "FDF2F2" },
      border: {
        left: { style: BorderStyle.SINGLE, size: 18, color: "C0392B", space: 8 },
        top: { style: BorderStyle.SINGLE, size: 2, color: "FDF2F2", space: 6 },
        bottom: { style: BorderStyle.SINGLE, size: 2, color: "FDF2F2", space: 6 },
        right: { style: BorderStyle.SINGLE, size: 2, color: "FDF2F2", space: 6 },
      },
      children: [R("Anti-pattern. ", { bold: true, color: "9B1C1C" }), R(d.anti_pattern)],
    }));
  }
  if (d.ceiling_rule) body.push(CALLOUT("Ceiling rule.", d.ceiling_rule));
  body.push(
    table(
      ["ID", "Sub-capability", "Weight", "The question"],
      d.subcapabilities.map(s => [s.id, s.name, s.weight + "%", s.question]),
      [800, 2500, 800, 4926],
      { boldFirstCol: true },
    ),
    CAPTION(`Table 5.${i + 1} — ${d.id} sub-capabilities. Full 0–5 descriptors are in Appendix A.`),
  );
  // narrative on the pivotal step for this domain
  const pivot = {
    TI: "The pivotal step in this domain is TI.4, extraction to procedure level. An organisation that tags reports with parent technique IDs has a searchable archive; an organisation that extracts the specific command line, API call or protocol behaviour has something a detection engineer can build from this afternoon. The difference between those two states is usually the difference between a threat intelligence function that is respected by engineering and one that is politely ignored.",
    TM: "The pivotal step is TM.3 and TM.4 taken together: moving from threat models as documents to attack trees and computed attack paths as structured, queryable data. Once trees are data, choke-point analysis becomes possible — identifying the nodes that appear across many trees and are therefore worth disproportionate detection investment. This is where a detection strategy stops being a list and starts being an argument.",
    DC: "The pivotal step is DC.2, telemetry quality. Almost every organisation believes its telemetry is fine, and almost none measures completeness, parsing success, ingestion latency and field-level fill rate per source. Silent telemetry failure is the most common cause of a detection that exists and cannot fire, and it is invisible until either someone measures it or an adversary benefits from it.",
    DE: "The pivotal step is DE.4, testing. It is the boundary between detection writing and detection engineering. Every other practice in this domain — version control, peer review, metadata, health monitoring — is more valuable once tests exist and considerably less valuable without them, because without a test there is no definition of the rule working.",
    AV: "There is no single pivotal step here; the domain is the pivot. But if one sub-capability predicts the rest, it is AV.7, the findings-to-closure loop. Organisations frequently run impressive exercises whose findings are never closed and never re-tested. An exercise whose output is a report is a spending event; an exercise whose output is a closed, re-tested gap is a capability improvement.",
    AA: "The pivotal step is AA.5, hunting, because hunting is the only sub-capability in the model that reliably produces new detection requirements from within the organisation rather than from external reporting. A hunting programme whose hypotheses come from the threat profile, threat models and validation gaps — and whose required output is a detection, a tuning change or an evidenced negative result — is a compounding asset.",
    IR: "The pivotal step is IR.6, the post-incident review, and specifically its hardest question: at what point in the timeline could we first have detected this, and why did we not? Answering that structurally every time, and then proving the answer has changed by re-emulating the incident, is the single most reliable route from operational experience to improved detection.",
    GV: "The pivotal step is GV.3, metrics. The metrics an organisation reports determine what it improves, and most report activity. Replacing alert counts with validated coverage, detection precision and time from adversary action to detection changes behaviour across every other domain — which is precisely why it is usually resisted.",
  }[d.id];
  body.push(H3("Where this domain turns"), P(pivot));
});

/* ---- ch 6: running an assessment ---- */
body.push(
  H1("6. Running an assessment", { pageBreak: true }),
  H2("6.1 Choose the assessment type"),
  table(
    ["Type", "Effort", "Confidence", "Use it when"],
    [
      ["Rapid self-assessment", "Half a day, 2–3 people", "Low. Directional only.", "You need a first baseline and a sense of where to look. Do not report the number outside the team."],
      ["Structured self-assessment", "2–3 days across 6–10 people, evidence gathered", "Moderate. Defensible internally.", "Annual planning, budget cases, board reporting with the assumptions stated."],
      ["Evidence-based assessment", "1–2 weeks, artefacts collected and reviewed against each claimed level", "High. Withstands challenge.", "Regulatory or contractual assurance, post-incident review, pre- and post-investment measurement."],
      ["Independent assessment", "2–4 weeks including validation sampling", "Highest. Includes spot-testing claims by emulation.", "Third-party assurance, acquisition due diligence, or when internal assessments have plateaued suspiciously."],
    ],
    [1900, 2200, 2100, 2826],
    { boldFirstCol: true },
  ),
  CAPTION("Table 6.1 — Assessment types. Confidence rises with the cost of the evidence, not with the seniority of the assessor."),
  H2("6.2 Who takes part"),
  P("An assessment scored by one person is an opinion. The minimum credible participation set is:"),
  BULLET("Threat intelligence lead — domains TI, and contributes to TM and AV."),
  BULLET("Security architect or threat modeller — domain TM."),
  BULLET("Detection platform or data engineering lead — domain DC."),
  BULLET("Detection engineering lead — domain DE."),
  BULLET("Purple team, red team or offensive security lead — domain AV. If no such role exists, that is itself a finding, and AV is unlikely to score above 1."),
  BULLET("SOC manager and senior analyst — domains AA and IR."),
  BULLET("Security leadership — domain GV, and sign-off on scope and exclusions."),
  P("Scores should be proposed by the accountable owner and challenged by at least one other participant. The challenge question is always the same and always the same three words: show me the artefact."),
  H2("6.3 Sequence"),
  NUM("Agree and record scope, exclusions and the threat profile reference. An assessment without a scope statement cannot be compared with anything, including itself six months later."),
  NUM("Define the in-scope ATT&CK technique set from platforms and threat profile. Record the rationale. This is the step most often skipped and most often regretted."),
  NUM("Score domains in order TI, TM, DC, DE, AV, AA, IR, GV. The order matters: scoring AV before the domains it caps tends to produce defensive scoring in the earlier domains."),
  NUM("Collect evidence references as you go, not afterwards. A claim you cannot evidence in the session will not become evidenceable later."),
  NUM("Run the scoring engine or the workbook, and read the constraint log before the scores. The constraint log tells you where the organisation's self-image and its evidence diverge."),
  NUM("Produce the two reports: the engineering roadmap ranked by weighted impact, and the executive summary stating what is and is not proven."),
  NUM("Set the re-assessment date. Annual is the minimum; semi-annual is better for a programme actively investing."),
  H2("6.4 Common failure modes in the assessment itself"),
  table(
    ["Failure", "How it shows up", "Counter"],
    [
      ["Scoring the intent", "‘We are doing that next quarter’ scored as if it were done.", "Score the present tense only. Put the intent in the target column, where it belongs."],
      ["Scoring the tool", "‘We have a BAS platform’ scored as Level 4 in AV.2.", "The descriptors ask about cadence, scope and drift alerting, not licences. Read them aloud."],
      ["Best-case scoring", "The best-instrumented business unit is described as if it were the estate.", "Score the scope as stated. If coverage is uneven, either narrow the scope or score to the weakest material part and note it."],
      ["Vocabulary drift", "‘Threat modeling’ meaning a risk workshop; ‘hunting’ meaning dashboard review.", "Use the level descriptors as the definition. They exist to settle exactly this argument."],
      ["Consensus averaging", "Disagreement resolved by splitting the difference.", "Disagreement is information. Record both scores and the evidence each side cites, then let the evidence decide."],
      ["Assessment as performance review", "Owners defending scores as if they were being appraised.", "State explicitly that a low score is a funding argument, not a failure. If that is not true in your organisation, the assessment will not be honest and you should commission an independent one."],
    ],
    [1900, 3300, 3826],
    { boldFirstCol: true },
  ),
  CAPTION("Table 6.2 — Assessment failure modes and their counters."),
);

/* ---- ch 7: scoring ---- */
body.push(
  H1("7. Scoring mechanics", { pageBreak: true }),
  H2("7.1 Rollup"),
  P("Sub-capability scores roll up to a domain score as a weighted mean over the in-scope sub-capabilities. Sub-capabilities marked not applicable are excluded from both numerator and denominator, so scoping something out neither helps nor harms the score — it simply removes it. Domain scores roll up to the overall score as a weighted mean using the domain weights."),
  P("The arithmetic is intentionally simple and fully transparent. A weighted mean is easy to explain to a board, easy to audit, and easy to reproduce independently. The three implementations shipped with the model — Python, Excel and JavaScript — produce identical results to two decimal places on the same input, and the test suite asserts this."),
  H2("7.2 Order of operations"),
  NUM("Apply C3 at sub-capability level: any score of 4 or 5 without a named evidence artefact becomes 3."),
  NUM("Compute raw domain scores as weighted means."),
  NUM("Apply C2: cap DE at DC + 1."),
  NUM("Apply C1: cap every other domain at the adjusted AV score + 1."),
  NUM("Compute the overall score from the adjusted domain scores."),
  NUM("Report the unadjusted score, the adjusted score and every adjustment made."),
  H2("7.3 Bands"),
  table(
    ["Overall score", "Band", "What it means in practice"],
    [
      ["0.00 – 0.99", "Level 0 — Absent", "There is no detection capability to speak of. Treat this as a build project, not an improvement project."],
      ["1.00 – 1.99", "Level 1 — Ad hoc", "Capability exists in individuals. It will not survive their departure, and it cannot be relied upon in a report."],
      ["2.00 – 2.99", "Level 2 — Repeatable", "Consistent operations driven by tooling defaults and compliance. The most populated band, and the one where spending most often outruns capability."],
      ["3.00 – 3.99", "Level 3 — Threat-Informed", "Work is driven by a prioritised adversary profile and traceable to it. A credible target for most organisations."],
      ["4.00 – 4.99", "Level 4 — Measured & Validated", "Claims are proven by emulation and trended over time. Realistic only with a standing validation function."],
      ["5.00", "Level 5 — Adaptive", "A closed, automated, measured loop that also contributes back. Rare, and should be treated with scepticism unless the evidence is exceptional."],
    ],
    [1500, 2200, 5326],
    { boldFirstCol: true },
  ),
  CAPTION("Table 7.1 — Overall maturity bands."),
  H2("7.4 Prioritisation arithmetic"),
  P("The roadmap ranks improvement actions by weighted impact: domain weight multiplied by sub-capability weight multiplied by the gap to target, scaled for readability. This ranking is intentionally mechanical. It prevents the roadmap from being driven by whichever capability its owner argued for most forcefully, and it produces the counter-intuitive but usually correct answer that a two-level gap in a heavily weighted sub-capability outranks a four-level gap in a lightly weighted one."),
  P("The ranking is a starting point, not an instruction. Dependencies matter — improving detection engineering before fixing telemetry quality wastes effort, which is why C2 exists — and the tooling surfaces the constraint log next to the roadmap so the sequencing argument is visible."),
);

/* ---- ch 8: tooling ---- */
body.push(
  H1("8. The toolkit", { pageBreak: true }),
  P("The model ships with working tools, because a maturity model distributed as a PDF becomes a spreadsheet somebody rebuilds badly."),
  SPACER(60),
  table(
    ["Artefact", "What it is", "Use it for"],
    [
      ["model/*.yaml", "The model itself: eight domain files plus metadata, fully machine-readable, with a JSON schema.", "Integration, automation, building your own tooling, proposing changes by pull request."],
      ["tidcmm (Python package)", "Loader, validator, scoring engine and CLI. Implements C1, C2, C3 and the Validated Coverage Score.", "Scoring in a pipeline, regression-testing your own assessments, generating reports as JSON."],
      ["TID-CMM-Self-Assessment.xlsx", "Eleven-tab workbook: setup, eight domain tabs with the full descriptors as cell comments, the complete ATT&CK technique list, a dashboard with radar chart, a ranked roadmap and a crosswalk.", "Running an assessment offline, in a workshop, with people who will not install anything."],
      ["tid-cmm-assessment.html", "A single self-contained file — no server, no CDN, no network traffic — with the full questionnaire, live scoring, radar chart, ATT&CK coverage tab, JSON import and export, CSV export and a print view.", "Distributed assessment, embedding in an intranet or the project site, sharing with a client without sending them a macro-enabled workbook."],
      ["data/attack_techniques.csv", `The normalised ATT&CK Enterprise v${attack.version} technique set with tactics, platforms, required data components and detection guidance.`, "Scoping the in-scope technique set, building Navigator layers, telemetry gap analysis."],
      ["assessments/", "A blank template and a fully worked example.", "Starting an assessment; understanding what a completed one looks like."],
    ],
    [2100, 4100, 2826],
    { boldFirstCol: true },
  ),
  CAPTION("Table 8.1 — What ships with the model."),
  H2("8.1 Privacy"),
  P("The browser tool holds everything in the page. It makes no network requests, loads no external resources and stores nothing outside the session. Export to JSON is the only way data leaves it. This is a deliberate design decision: assessment data is a detailed map of an organisation's blind spots, and it should not traverse a third party's infrastructure to be scored."),
  H2("8.2 Consistency between implementations"),
  P("The Python engine, the Excel workbook and the browser tool implement the same arithmetic independently. The test suite asserts agreement between them on the worked example to two decimal places, including the constraint log. This matters because the three will be used by different people in the same organisation, and a discrepancy would undermine the assessment more effectively than any methodological criticism."),
);

/* ---- ch 9: worked example ---- */
const ex = REPORT;
body.push(
  H1("9. Worked example", { pageBreak: true }),
  P(`This chapter works through a complete assessment for an illustrative organisation, ${ex.organisation.replace(" (illustrative example)", "")} — a mid-sized financial services group with a mature, well-funded security operations function. The figures are constructed, but the shape is drawn from a pattern that recurs constantly: strong operations, weak validation, and a self-assessment that does not survive the constraints.`),
  H2("9.1 Scope"),
  P("Group SOC covering the UK and EU entities. The recently acquired payments subsidiary and the OT estate at two manufacturing sites are explicitly excluded, with the residual risk accepted by the group risk committee. The in-scope ATT&CK technique set is 581 of 697 techniques, derived from the platform mix (Windows, Linux, macOS, IaaS, SaaS, identity provider, office suite, containers)."),
  H2("9.2 Results"),
  table(
    ["Domain", "Self-assessed", "Adjusted", "Band", "Constraint applied"],
    ex.domains.map(d => [
      `${d.id} — ${d.name}`,
      d.raw_score.toFixed(2),
      d.score.toFixed(2),
      d.band.replace("Level ", "L").replace(" — ", " "),
      d.adjustments.length ? "C1 validation ceiling" : "—",
    ]).concat([[
      "OVERALL", ex.overall_raw.toFixed(2), ex.overall_score.toFixed(2),
      ex.overall_band.replace("Level ", "L").replace(" — ", " "), "",
    ]]),
    [3200, 1500, 1400, 1700, 1226],
    { boldFirstCol: true },
  ),
  CAPTION("Table 9.1 — Domain results. Four domains were capped by the validation ceiling."),
  P(`The organisation self-assesses at ${ex.overall_raw.toFixed(2)}. After constraints it scores ${ex.overall_score.toFixed(2)}. The ten-hundredths difference is not the interesting part; the constraint log is:`),
  SPACER(60),
  ...ex.constraint_log.map(l => P(l, { size: 19, color: "9B1C1C", after: 60, indent: { left: convertInchesToTwip(0.3) } })),
  SPACER(120),
  P("Four domains — telemetry, detection engineering, analytics and incident response — were all capped at the same value, 2.63, by the same cause: an adversarial validation score of 1.63. The organisation has built a great deal and proven very little of it. This is the finding. Everything else in the assessment is detail."),
  H2("9.3 Coverage"),
  P("Against the 581 in-scope techniques, the Validated Coverage Score is 47.4%. Decomposed: 48.9% of in-scope techniques have detection logic deployed, but only 12.7% have been proven to fire by emulation, and 19.3% have no telemetry at all."),
  CALLOUT("Read that decomposition carefully.", "The organisation would, on the standard industry metric, report roughly 49% ATT&CK coverage — a respectable number that would pass without challenge in most board packs. The proportion it has actually proven is 12.7%. The gap between those two figures is the entire argument for this model."),
  H2("9.4 The roadmap"),
  table(
    ["Impact", "ID", "Sub-capability", "Now", "Target"],
    ex.priorities.slice(0, 10).map(p => [
      p.impact.toFixed(1), p.subcapability_id, p.name, String(p.current), String(p.target),
    ]),
    [1000, 900, 5126, 1000, 1000],
    { boldFirstCol: true },
  ),
  CAPTION("Table 9.2 — Top ten improvement actions by weighted impact."),
  P("The ranking is unambiguous and it is not what the organisation expected. Six of the top ten items sit in threat modeling and adversarial validation — the two domains that did not exist in the organisation's previous framework and had therefore never been assessed, resourced or reported. Not one of the top ten is a tooling purchase."),
  H2("9.5 What the CISO is told"),
  P([R("“", { size: 21, color: MUTED }), R("We are at 2.34 on a five-point scale, in the Repeatable band. Our operations are sound: telemetry, detection engineering, analytics and incident response all sit close to Level 3 on their own merits. The number is held down by one thing. We have never systematically tested whether our detection works against the adversaries we say we care about, so four of our eight domains are capped by our validation score. On the coverage measure, we have detection logic for about half the techniques relevant to our estate, and we have proven about one in eight. The single highest-return investment available to us is a standing purple team and emulation capability. It will raise four domains at once, it will tell us which of the detection we already own is real, and it costs materially less than the platform renewal we are being asked to approve this quarter.", { size: 21 }), R("”", { size: 21, color: MUTED })], { indent: { left: convertInchesToTwip(0.35), right: convertInchesToTwip(0.35) }, }),
  P("That paragraph is defensible, specific, and leads to a decision. It is also, by construction, impossible to write from alert volumes."),
);

/* ---- ch 10: adoption ---- */
body.push(
  H1("10. Adoption", { pageBreak: true }),
  H2("10.1 A first ninety days"),
  NUM("Week 1 — Run a rapid self-assessment with the browser tool to get a baseline. Do not report it. Its purpose is to show you which conversations you need to have."),
  NUM("Weeks 2–3 — Define the in-scope technique set properly. This is the highest-value fortnight in the programme, because everything downstream is measured against it."),
  NUM("Weeks 4–6 — Run a structured assessment with evidence, using the workbook, with the participation set from Chapter 6. Record every artefact reference."),
  NUM("Weeks 7–8 — Publish the two reports. Take the constraint log to leadership before the score; it is the part that changes decisions."),
  NUM("Weeks 9–12 — Start the top three roadmap items. If AV is your binding constraint, start with atomic testing (AV.1) — it is the cheapest sub-capability in the domain and it will immediately tell you which of your existing detection is real."),
  H2("10.2 Setting a target"),
  P("Level 5 is not a target for most organisations, and treating it as one produces theatre. A defensible target for a well-resourced enterprise is 3.5 to 4.0 overall, with adversarial validation at 4.0 or above so that it stops being the binding constraint. For a smaller organisation, 2.5 to 3.0 with an honest, narrow in-scope technique set is a stronger position than 3.5 over a scope chosen to flatter."),
  P("Set the target per domain, not globally. The model's tooling supports this, and it forces the useful conversation: which of these eight things do we actually need to be excellent at, given who is attacking us?"),
  H2("10.3 Re-assessment"),
  P("Annually at minimum. Semi-annually if you are actively investing, because you need to be able to attribute movement to the investment. Keep the scope and the in-scope technique set stable between assessments; if either changes, say so explicitly and report both the like-for-like and the new-basis figures. A maturity score that moves because the scope moved is worse than no score."),
  H2("10.4 Contributing"),
  P(`The model is open and versioned at ${MODEL.model.repository}. Level descriptors, weights, crosswalks and the in-scope scoping guidance are all open to challenge by pull request. Anonymised assessment data, sector benchmarks and additional crosswalks are all welcome. The model will move to v1.1 on the first substantive change to any descriptor, and every version is tagged so an assessment can state which version produced it.`),
  H2("10.5 Licence"),
  P(`Model content is licensed CC-BY-4.0; code and tooling are Apache-2.0. Commercial use is permitted, including by vendors implementing the model in products, provided attribution is retained. Assessments are self-declared: there is no certification scheme, and any claim of a certified TID-CMM level should be treated as marketing.`),
);

/* ---- appendix A ---- */
body.push(H1("Appendix A — Full sub-capability register", { pageBreak: true }));
body.push(P("Generated from the machine-readable model. Every sub-capability with its weight, assessment question, complete 0–5 descriptors and the evidence that would justify a high score.", { italics: true, color: MUTED, size: 19 }));
MODEL.domains.forEach(d => {
  body.push(H2(`${d.id} — ${d.name} (${d.weight}%)`, { pageBreak: true }));
  d.subcapabilities.forEach(s => {
    body.push(
      H3(`${s.id}  ${s.name}   ·   weight ${s.weight}%`),
      P([R("Question. ", { bold: true, size: 19 }), R(s.question, { size: 19 })], { after: 100 }),
      table(
        ["L", "Descriptor"],
        [0, 1, 2, 3, 4, 5].map(lv => [String(lv), s.levels[lv]]),
        [600, 8426],
        { boldFirstCol: true, size: 17 },
      ),
      P([R("Evidence. ", { bold: true, size: 18, color: MUTED }), R((s.evidence || []).join("  ·  "), { size: 18, color: MUTED })], { before: 80, after: 240 }),
    );
  });
});

/* ---- appendix B ---- */
body.push(
  H1("Appendix B — Framework crosswalk", { pageBreak: true }),
  P("Indicative mapping at sub-capability level, so a TID-CMM assessment can feed existing NIST CSF 2.0 and SOC-CMM reporting without a second exercise. Mappings are one-to-many in both directions and are not a claim of equivalence.", { italics: true, color: MUTED, size: 19 }),
  table(
    ["ID", "Sub-capability", "NIST CSF 2.0", "SOC-CMM", "Other"],
    MODEL.domains.flatMap(d => d.subcapabilities.map(s => [
      s.id, s.name,
      (s.crosswalk.nist_csf_2 || []).join(", "),
      (s.crosswalk.soc_cmm || []).join(", "),
      Object.entries(s.crosswalk).filter(([k]) => !["nist_csf_2", "soc_cmm"].includes(k))
        .map(([k, v]) => `${k}: ${v.join(", ")}`).join(" | "),
    ])),
    [700, 2300, 2400, 2200, 1426],
    { size: 16, boldFirstCol: true },
  ),
);

/* ---- appendix C ---- */
body.push(
  H1("Appendix C — ATT&CK alignment and scoping", { pageBreak: true }),
  P(`This version of the model is aligned to MITRE ATT&CK Enterprise v${attack.version}, snapshot ${attack.snapshot_date}.`),
  table(
    ["Element", "Count"],
    [
      ["Tactics", String(attack.tactics)],
      ["Techniques (total)", String(attack.techniques)],
      ["Parent techniques", String(attack.parent_techniques)],
      ["Sub-techniques", String(attack.sub_techniques)],
      ["Data components", String(attack.data_components)],
    ],
    [5000, 4026],
    { boldFirstCol: true },
  ),
  CAPTION("Table C.1 — ATT&CK Enterprise content at the aligned version."),
  H2("Scoping the in-scope technique set"),
  P("The in-scope set is the techniques an organisation could plausibly experience and has decided to measure itself against. Build it in this order:"),
  NUM("Filter by platform. Remove techniques that target platforms you do not operate. This is objective and usually removes 15–25% of the matrix."),
  NUM("Filter by threat profile. Retain techniques used by the actors and campaigns you ranked as relevant, plus techniques on the attack paths to your crown jewels regardless of attribution."),
  NUM("Add back anything that appears in your attack trees. A technique nobody has publicly attributed to your adversaries but which sits on a short path to your crown jewels belongs in scope."),
  NUM("Record every exclusion with a reason. The exclusion list is an assessment artefact and should be reviewed at every re-assessment, because platforms change faster than threat profiles."),
  P("Do not scope by ease of detection. Excluding techniques because they are hard to see is the precise failure this model exists to prevent."),
  H2("On ATT&CK version changes"),
  P("ATT&CK is versioned and moves several times a year. Techniques are added, deprecated, merged and revoked. Re-baseline the in-scope set on each major release, report the diff, and note that a coverage score computed against a different ATT&CK version is not directly comparable. The workbook and the tooling both state the aligned version prominently for this reason."),
);

/* ---- appendix D ---- */
body.push(
  H1("Appendix D — Glossary", { pageBreak: true }),
  table(
    ["Term", "As used in this model"],
    [
      ["Adversarial validation", "Any activity that executes adversary behaviour against the defended environment to test whether it is prevented, seen, detected or responded to. Spans atomic testing, BAS, emulation, purple teaming, penetration testing and red teaming."],
      ["Attack path", "A computed sequence of steps through the real estate — identity relationships, entitlements, network reachability, trust — by which an adversary could reach a crown jewel from a given starting position."],
      ["Attack tree", "A decomposition of an adversary objective into the alternative branches by which it could be achieved, with nodes mapped to ATT&CK techniques and leaves carrying a prevent, detect or accept decision."],
      ["Choke point", "A node appearing across many attack trees or paths, and therefore worth disproportionate detection or prevention investment."],
      ["Crown jewel", "An asset, dataset, identity or process whose compromise would cause material business harm, identified through business impact analysis rather than by technical criticality alone."],
      ["Detection-as-code", "Managing detection content with software engineering practice: version control, peer review, automated testing, CI/CD deployment and drift detection."],
      ["Emulation plan", "A sequenced set of techniques reproducing a specific adversary's tradecraft against a realistic objective, as opposed to isolated technique execution."],
      ["In-scope technique set", "The subset of ATT&CK techniques an organisation measures itself against, derived from its platforms and prioritised threat profile, with the rationale recorded."],
      ["Silent failure", "A detection that no longer works because its data stopped arriving, its schema changed, or its schedule broke — while continuing to appear enabled and healthy."],
      ["Threat profile", "The ranked, evidenced set of adversaries, campaigns and behaviours most relevant to a specific organisation, derived from sector, geography, technology and exposure."],
      ["Validated Coverage Score", "Achieved points over maximum available across the in-scope technique set, on the 0–3 scale in Table 4.3, expressed as a percentage."],
      ["Strict mode", "Scoring with the three integrity constraints applied. The default, and the only mode in which a score should be reported externally."],
    ],
    [2000, 7026],
    { boldFirstCol: true },
  ),
);

/* ---- back page ---- */
body.push(
  new Paragraph({ children: [new PageBreak()] }),
  SPACER(2400),
  P([R("TID-CMM", { size: 46, bold: true, color: NAVY })], { align: AlignmentType.CENTER, after: 80 }),
  P([R("Threat-Informed Detection Capability Maturity Model", { size: 22, color: ACCENT })], { align: AlignmentType.CENTER, after: 400 }),
  P([R(`Version ${MODEL.model.version}  ·  ${MODEL.model.released}`, { color: MUTED })], { align: AlignmentType.CENTER, after: 60 }),
  P([R(MODEL.model.homepage, { color: ACCENT })], { align: AlignmentType.CENTER, after: 40 }),
  P([R(MODEL.model.repository, { color: ACCENT })], { align: AlignmentType.CENTER, after: 40 }),
  P([R(MODEL.model.contact, { color: ACCENT })], { align: AlignmentType.CENTER, after: 300 }),
  P([R("Model content CC-BY-4.0  ·  Tooling Apache-2.0", { color: MUTED, size: 18 })], { align: AlignmentType.CENTER, after: 200 }),
  P([R("MITRE ATT&CK® is a registered trademark of The MITRE Corporation. This work is not affiliated with or endorsed by MITRE, NIST or SOC-CMM.", { color: MUTED, size: 16, italics: true })], { align: AlignmentType.CENTER }),
);

/* ------------------------------------------------------------- document */
const doc = new Document({
  creator: "Reza Adineh",
  lastModifiedBy: "Reza Adineh",
  title: "TID-CMM — Threat-Informed Detection Capability Maturity Model",
  description: "A framework for measuring threat-informed detection capability.",
  keywords: "detection engineering, MITRE ATT&CK, maturity model, security operations",
  subject: "Threat-Informed Detection Capability Maturity Model",
  styles: {
    default: {
      document: { run: { font: FONT, size: 21, color: INK }, paragraph: { spacing: { line: 276 } } },
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: NAVY } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 25, bold: true, color: ACCENT } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 22, bold: true, color: ACCENT } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.3), hanging: convertInchesToTwip(0.18) } } } },
        { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.6), hanging: convertInchesToTwip(0.18) } } } },
      ]},
      { reference: "numbers", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.35), hanging: convertInchesToTwip(0.22) } } } },
      ]},
    ],
  },
  sections: [{
    properties: { page: { margin: { top: 1200, right: 1200, bottom: 1100, left: 1200 } } },
    headers: {
      default: new Header({ children: [new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 4 } },
        children: [
          R("TID-CMM — Threat-Informed Detection Capability Maturity Model", { size: 16, color: MUTED }),
          new TextRun({ children: [new PositionalTab({
            alignment: PositionalTabAlignment.RIGHT, relativeTo: "margin", leader: PositionalTabLeader.NONE })] }),
          R(`v${MODEL.model.version}`, { size: 16, color: MUTED }),
        ],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES],
                                 font: FONT, size: 16, color: MUTED })],
      })] }),
    },
    children: body,
  }],
});

const out = process.argv[2] || path.join(ROOT, "build", "TID-CMM-White-Paper-v1.0.docx");
Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, buf);
  console.log(`${out}  (${(buf.length / 1024).toFixed(0)} KB)`);
});
