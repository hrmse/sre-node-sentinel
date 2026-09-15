# Operations guide

## Service lifecycle

```bash
systemctl status sre-node-sentinel.timer
systemctl list-timers sre-node-sentinel.timer
systemctl start sre-node-sentinel.service
journalctl -u sre-node-sentinel.service --since '1 hour ago'
```

The service returns exit status `1` when a policy control fails. systemd will
record this as a failed invocation even though the metrics file is still
written. Treat that as an expected signal and inspect the rendered metric or
run the command interactively before changing a policy.

## Policy change process

1. Add or modify a check in source control and add a filesystem-fixture test
   if parser behavior changes.
2. Test against a representative non-production host or mounted image.
3. Review the expected state with the platform/security owner.
4. Deploy with Ansible and watch `unknown` and `fail` metrics before enabling
   paging.
5. Record the policy version/change in your change-management system.

## Distribution compatibility

The role expects systemd, Python 3, and node_exporter textfile collector
support. `/usr/sbin/nologin` and package names can differ by distribution;
override role variables or adapt the role after testing in your target OS
matrix. Do not run it unreviewed on immutable or container host images.
