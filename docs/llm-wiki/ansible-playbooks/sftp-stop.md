---
type: Playbook
title: sftp_stop.yml
description: Stops the sftpgo service on the SFTP hosts and disables it at boot.
resource: /playbooks/sftp_stop.yml
tags: [sftp, sftpgo, service]
timestamp: 2026-09-17T00:00:00Z
---

`sftp_stop.yml` has one play on `sftp` with `become: true`, tagged
`no_testing`, that sets the `sftpgo` service to `stopped` and not `enabled`.
The counterpart is [sftp_start.yml](/ansible-playbooks/sftp-start.md). See
[SFTP](/components/sftp.md).

There is no `playbooks/tests/sftp_stop.yml`.

# Citations

[1] `playbooks/sftp_stop.yml` — the playbook.
