# The Eight TID-CMM Domains

The canonical TID-CMM model contains eight weighted domains totalling 100%.

| ID | Domain | Weight | Sub-capabilities | Core question |
| --- | --- | ---: | ---: | --- |
| TI | Threat Intelligence & Adversary Prioritisation | 12% | 6 | Who are we defending against, and how do we know? |
| TM | Threat Modeling & Attack Path Analysis | 12% | 7 | What do their behaviours look like against our architecture? |
| DC | Telemetry & Detection Coverage | 14% | 6 | Can we see the activity at all? |
| DE | Detection Engineering | 16% | 10 | Do we build, test and maintain detection like engineers? |
| AV | Adversarial Validation & Emulation | 14% | 8 | Have we proven any of it works? |
| AA | Analytics, Automation & Hunting | 12% | 8 | Does detection output become a decision at operational tempo? |
| IR | Incident Response & Recovery | 10% | 6 | Can we act on what we detect? |
| GV | Governance, Metrics & Continuous Improvement | 10% | 7 | Is this directed, measured and sustainable? |

The IR domain is deliberately narrow. In current TID-CMM it measures the **detection-to-response interface**: whether an alert reaches responders correctly, whether case data is sufficient, and whether incident learning feeds back into detection. Full response capability is measured by TIR-CMM.

Canonical site: https://tid-cmm.com