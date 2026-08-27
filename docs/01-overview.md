# TID-CMM Overview

TID-CMM is the **Threat-Informed Detection Capability Maturity Model**. It measures whether a detection programme is genuinely driven by adversary behaviour, whether the organisation has the telemetry needed to observe that behaviour, and whether the claimed capability has been proven to work.

It does not measure success by the number of deployed rules or by ATT&CK coverage percentages alone. A mapped detection can still be ineffective when the required data is missing, the detection has never been validated, or the covered technique is irrelevant to the organisation's actual threat profile.

The current canonical model is **1.5.0**, with 8 domains, 58 sub-capabilities and 348 level descriptors, aligned to MITRE ATT&CK Enterprise v19.2.

## Core questions

- Who are we defending against, and how do we know?
- Which crown jewels and attack paths matter?
- Which ATT&CK behaviours are relevant to those paths?
- Can the organisation actually observe those behaviours?
- Is telemetry complete, healthy and trustworthy?
- Are detections engineered, tested and maintained?
- Has adversarial validation proven the capability?
- Does detection output become an operational decision?
- Does response feed learning back into detection?
- Can the organisation demonstrate capability with evidence?

## What TID-CMM is not

TID-CMM is not a certification scheme, a vendor scorecard, a SIEM product comparison, or a replacement for MITRE ATT&CK, NIST CSF, SOC-CMM or UTIOM.

It is a measurement instrument for the detection capability already defined inside the wider UTIOM operating model.

Canonical site: https://tid-cmm.com