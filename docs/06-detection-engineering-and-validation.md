# Detection Engineering and Validation

TID-CMM treats detection content as an engineering product rather than a collection of rules.

Mature practice includes version control, peer review, explicit intent, testing, lifecycle ownership, validation and feedback from incidents. Detection should be traceable to the threat and attack-path reasoning that justified it.

Validation is not optional evidence added after deployment. It is the mechanism that proves whether the detection chain actually works.

**Threat driver → attack path → required telemetry → detection logic → test → alert → analysis → operational handoff**

The Adversarial Validation & Emulation domain exists because an untested capability remains an assumption. Purple teaming, adversary emulation and detection QA should therefore be used to test both individual behaviours and meaningful attack scenarios.

TID-CMM distinguishes detection intent from maturity. A decisive single-event detection is not inherently less mature than a multi-stage analytic, and a hunting/context signal is not expected to behave like a decisive alert. The model's public detection classes are intended to keep those expectations explicit.

Canonical site: https://tid-cmm.com