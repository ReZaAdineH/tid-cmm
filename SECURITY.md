# TID-CMM Security Policy and Vulnerability Reporting

TID-CMM includes a public model repository, machine-readable data and a browser-based assessment tool. Security findings should be reported privately.

## Report privately

**Do not publish a suspected vulnerability, exploit, credential, sensitive endpoint, assessment data exposure, or reproduction containing sensitive data in a public Issue or Discussion.**

Preferred reporting paths:

1. If GitHub displays **Report a vulnerability** in this repository's Security area, use that private channel.
2. Otherwise contact **hello@tid-cmm.com** or use the security/contact guidance on https://tid-cmm.com.

## In scope

Examples include:

- vulnerabilities in the public assessment tool or canonical website;
- unintended transmission or exposure of assessment answers despite the browser-local design;
- cross-site scripting, injection, unsafe file import/export or similar web weaknesses;
- accidental exposure of credentials, tokens, private keys, private endpoints or non-public implementation details;
- integrity weaknesses in downloadable model/data artifacts;
- malicious or unsafe parsing of public model/export formats;
- repository content that accidentally discloses private operational material.

## Public Issues are appropriate for

- descriptor/model defects that are not security vulnerabilities;
- ATT&CK/data mapping errors;
- documentation errors;
- broken public links;
- scoring questions and counter-examples that contain no sensitive information.

## Safe-testing boundaries

Please do not access data that is not yours, perform denial-of-service or resource-exhaustion testing, use social engineering, establish persistence, move laterally, or perform broad automated scanning that could degrade the service.

If sensitive data is encountered, stop, retain only the minimum evidence needed, and report privately.

## Coordinated disclosure

Please allow a reasonable period for investigation and remediation before public disclosure. There is currently no bug-bounty promise associated with a report.

## Public/private boundary

The public model and data are intentionally open under their stated licences. The assessment tool may be free to use without being licensed for redistribution, and private production implementation, credentials and operational infrastructure remain outside the public repository.