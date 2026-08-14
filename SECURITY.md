# Security policy

## Reporting a vulnerability

Email **hello@tid-cmm.com**. Please allow 90 days before public disclosure.

Include what you found, how to reproduce it, and what an attacker could achieve. A working
proof of concept helps but is not required.

## What is in scope

TID-CMM is a static site and a browser-only tool. There is no backend, no database, no
authentication and no server-side code, so the interesting surface is narrow:

- **Cross-site scripting** in the assessment tool, particularly through an imported
  assessment JSON or a poisoned `localStorage` entry. This is the one path where untrusted
  data reaches the renderer, and it is the area we care about most.
- **Content injection** via the published datasets or model files.
- **Supply chain** — the build scripts, or the ATT&CK data ingestion.
- Weaknesses in the published security headers or Content-Security-Policy.

## What is not in scope

- Anything requiring the victim to paste attacker-supplied JavaScript into their own console
- Missing headers on third-party hosts we do not control
- Automated scanner output with no demonstrated impact
- Social engineering, physical access, denial of service against the CDN

## Design commitments

These are properties we intend to hold. A report demonstrating any of them is false is a
valid finding:

- The assessment tool makes **no network requests**. Assessment data never leaves the
  visitor's browser.
- No cookies, no analytics, no third-party scripts, no external fonts or CDNs.
- Imported assessment data is coerced to a known schema before it reaches application state.
- `Content-Security-Policy` sets `connect-src 'none'`, so exfiltration is blocked at the
  browser even if injection were achieved.

## Known accepted risk

The Content-Security-Policy permits `script-src 'unsafe-inline'` because the tool uses inline
event handlers. Injection vectors are closed at the input boundary and `connect-src 'none'`
prevents exfiltration, so the residual risk is limited to same-page defacement. Removing
`unsafe-inline` requires migrating to event delegation and is tracked as planned work.
