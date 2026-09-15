# Architecture and design decisions

## Data flow

1. A team reviews a YAML policy alongside its Ansible configuration.
2. Ansible installs a pinned package, a restricted policy file, a service unit,
   and a periodic timer.
3. The service evaluates only local configuration and writes a Prometheus file
   using write-then-rename semantics.
4. node_exporter serves the file to Prometheus; dashboards and alerts consume
   the resulting status metrics.
5. An operator investigates drift and makes a separately reviewed Ansible
   change. The auditor remains read-only.

## Design choices

**Read-only and no shell.** The engine uses Python file APIs; policy values are
never interpolated into a command. This reduces attack surface and makes test
fixtures equivalent to a mounted image root.

**Unknown is a first-class state.** A missing directive, offline mount table,
or unsupported check cannot prove compliance. Exporting `unknown` avoids false
green dashboards and distinguishes instrumentation gaps from drift.

**Textfile collector, not a listener.** There is no additional HTTP server or
port to secure. Existing node_exporter authentication and network controls
continue to be the scrape boundary.

**Ansible remediates; Sentinel observes.** Combining drift detection and
automatic correction can erase evidence and create loops during an incident.
This repository keeps the two responsibilities separate.

## Non-goals

- Parsing every SSH `Include` and `Match` semantic.
- Replacing distribution-specific security hardening standards.
- Managing node_exporter installation or Prometheus RBAC.
- Automatically editing SSH, sysctl, fstab, or systemd configuration.
