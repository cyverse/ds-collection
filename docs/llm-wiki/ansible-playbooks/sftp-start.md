---
type: Playbook
title: sftp_start.yml
description: Starts the sftpgo service on the SFTP hosts and enables it at boot.
resource: /playbooks/sftp_start.yml
tags: [sftp, sftpgo, service]
timestamp: 2026-09-17T00:00:00Z
---

`sftp_start.yml` has one play on `sftp` with `become: true`, tagged
`no_testing`, that sets the `sftpgo` service to `started` and `enabled`. The
counterpart is [sftp_stop.yml](/ansible-playbooks/sftp-stop.md). See
[SFTP](/components/sftp.md).

There is no `playbooks/tests/sftp_start.yml`.

# Citations

[1] `playbooks/sftp_start.yml` — the playbook.
