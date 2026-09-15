# Threat model

## Assets

- Integrity of baseline policy and Ansible deployment artifacts.
- Integrity of the exported `.prom` file consumed by node_exporter.
- Availability of the periodic audit and its observability path.
- Confidentiality of configuration paths and posture disclosed by metrics.

## Trust boundaries and mitigations

| Boundary | Threat | Control in this repository |
| --- | --- | --- |
| Git to automation | Unreviewed policy weakens a control | PR CI, dependency review, protected-branch recommendation |
| Ansible controller to host | Package substitution or unexpected version | Explicit package variable; use approved internal index and version pinning |
| Policy parser to host | Command/config injection | `yaml.safe_load`, validation, no subprocess or shell execution |
| Service to filesystem | Accidental or malicious mutation | `ProtectSystem=strict`, read-only design, narrow `ReadWritePaths` |
| Metrics file to scraper | Partial or forged scrape | Atomic replace, directory ownership, node_exporter scrape boundary |

## Residual risks

A root-equivalent attacker can alter configuration, metrics, service units, or
the exporter. This project detects neither kernel compromise nor fraudulent
metrics from a compromised node. Use host attestation, centralized logging,
restricted deployment credentials, and independent security monitoring where
those risks matter.
