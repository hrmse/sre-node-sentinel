# Monitoring and alert design

The exporter supplies an explicit pass/fail/unknown state per check. Keep the
policy name and check IDs stable: changing labels creates new time series and
can invalidate alert references.

## Example Prometheus rules

```yaml
groups:
  - name: sre-node-sentinel
    rules:
      - alert: LinuxBaselineControlFailing
        expr: sre_node_sentinel_check_status{status="fail"} == 1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Linux baseline control is failing on {{ $labels.instance }}"
          runbook_url: "https://github.com/REPLACE_WITH_OWNER/sre-node-sentinel/blob/main/docs/runbooks/control-failure.md"
```

Tune alert severity outside the metric label set; otherwise a policy edit can
silently alter routing. For high-severity controls, use a separate rule with
an explicit check allow-list after your team agrees on its response process.

## Suggested dashboard panels

- Failed checks by instance: `sum by (instance) (sre_node_sentinel_check_status{status="fail"})`
- Unknown checks by policy: `sum by (policy) (sre_node_sentinel_check_status{status="unknown"})`
- Fleet compliance percentage: `100 * sum(sre_node_sentinel_check_status{status="pass"}) / sum(sre_node_sentinel_check_status)`

The percentage is a signal, not a compliance attestation: checks have varying
criticality and unknown controls may be excluded from the business measure.
