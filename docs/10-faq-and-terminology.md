# TID-CMM FAQ and Terminology

## What does TID-CMM stand for?

**Threat-Informed Detection Capability Maturity Model.**

## What question does it answer?

**Would we actually see the adversaries most likely to attack us?**

## Is TID-CMM a certification?

No. TID-CMM does not operate a certification scheme. Assessments are self-declared unless independently reviewed at evidence-based depth.

## Is it a MITRE ATT&CK coverage score?

No. ATT&CK provides the behavioural vocabulary and data relationships. TID-CMM scopes relevant behaviours using the organisation's threat profile, crown jewels and attack paths, then measures whether the evidence, detections and validation exist.

## What is Telemetry Assurance?

A determination of whether the evidence required to observe an in-scope adversary behaviour is actually present, sufficiently deployed and trustworthy. Public reporting uses the terms **Assured, Partial, Weak and Blind**.

## What is Detection QA?

The testing and assurance discipline used to prove that detection logic, telemetry, alerting and downstream handling behave as intended rather than merely existing in configuration.

## What is the Validated Coverage Score?

A separate coverage metric showing how far in-scope ATT&CK behaviours have progressed from no telemetry through detection logic to validated detection. It is reported alongside maturity rather than substituted for it.

## Why does TID-CMM use attack paths?

Because a technique without architectural and business context does not explain whether an adversary could reach something important. Attack paths connect relevant behaviour to crown-jewel objectives.

## How does TID-CMM relate to UTIOM?

UTIOM is the operating model. TID-CMM is a deeper measurement instrument for the Threat Visibility and Threat Detection capabilities inside UTIOM's Engineering & Enablement pillar.

## How does TID-CMM relate to TIR-CMM?

TID-CMM asks whether you would see the attack. TIR-CMM asks whether you could act on it and contain it in time. The models are complementary and deliberately avoid duplicating each other's core domains.

Canonical site: https://tid-cmm.com