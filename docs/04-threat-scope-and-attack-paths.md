# Threat Scope, Crown Jewels and Attack Paths

TID-CMM is threat-informed by design. It does not begin by asking how much of MITRE ATT&CK is covered. It begins by asking which adversaries are relevant, which business-critical assets and services matter, and how those adversaries could reach them.

The canonical logic is:

**sector and geography → candidate adversaries → organisation-reviewed threat profile → crown jewels → threat models → attack paths → in-scope ATT&CK behaviours**

The assessment tool may suggest adversaries based on ATT&CK-documented targeting, but it does not select them on behalf of the organisation. Constraint C5 exists specifically to prevent a tool-generated profile from being treated as independently established threat intelligence.

Attack paths are important because a technique only matters operationally in context. TID-CMM therefore treats ATT&CK as a behavioural language inside a broader architecture- and business-driven model, not as a checklist to complete.

This aligns directly with UTIOM's principles: strategy before sensors, crown jewels drive prioritisation, and relevant threats shape architecture.

Canonical site: https://tid-cmm.com