# Runbook: Sentinel metrics are missing or stale

## Symptoms

The `up` target is healthy but `sre_node_sentinel_*` is absent, or values are
older than the configured timer cadence plus scrape delay.

## Checks

1. Verify the timer is enabled and scheduled:
   `systemctl list-timers sre-node-sentinel.timer`.
2. Inspect the last invocation and journal:
   `systemctl status sre-node-sentinel.service`.
3. Confirm the textfile directory matches node_exporter's
   `--collector.textfile.directory` and that the `.prom` file is readable by
   node_exporter.
4. Run `node_exporter`'s metrics endpoint locally through the approved access
   method and search for `sre_node_sentinel`.
5. Review systemd sandbox denials in the journal. A new policy path may be
   outside the service's permitted read view.

## Resolution

Fix the package, policy syntax, service permissions, or textfile directory
through Ansible. Validate a manual invocation, then allow one scheduled run
and a Prometheus scrape before resolving the incident.
