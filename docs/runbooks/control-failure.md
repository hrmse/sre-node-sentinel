# Runbook: Linux baseline control failure

## Trigger

`LinuxBaselineControlFailing` fires for 15 minutes or a dashboard shows a
failed Sentinel control.

## Triage

1. Identify `instance`, `policy`, and `check` labels from the alert.
2. Confirm the most recent service attempt:
   `systemctl status sre-node-sentinel.service` and
   `journalctl -u sre-node-sentinel.service --since '1 hour ago'`.
3. Run the auditor manually with JSON output on the host. Compare `expected`,
   `observed`, and `detail`; do not treat the metric alone as proof.
4. Determine whether this is intentional change, drift, unsupported platform
   behavior, or a policy/parser issue. Check the deployed policy checksum and
   recent Ansible/Git changes.

## Mitigation

For unintended drift, restore the approved configuration through the normal
Ansible change process. For an intentional exception, document scope and
expiry, then make a reviewed policy decision. Do not delete the metric file or
disable the timer merely to clear an alert.

## Escalation and closure

Escalate high-severity SSH or kernel-control failures according to the team's
security incident procedure. Close after a fresh service invocation exports
the expected status and the change record contains the cause and remediation.
