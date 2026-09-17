---
type: Playbook
title: irods_s3_cred.yml
description: Deploys the S3 credential files iRODS uses to reach S3 buckets into /etc/irods/s3-credentials and removes credential files that are no longer listed.
resource: /playbooks/irods_s3_cred.yml
tags: [irods, s3, credentials]
timestamp: 2026-09-17T00:00:00Z
---

`irods_s3_cred.yml` targets `irods` with `become: true`.

## What it does

1. Creates `/etc/irods/s3-credentials`, owned by the service account and
   group with mode `u+rx`.
2. Deletes any file in that directory whose name isn't an entry `name` in
   `_irods_s3_cred`.
3. Writes one file per `_irods_s3_cred` entry, named after the entry, with
   `access_key` on the first line and `secret_key` on the second. Files are
   owned by the service account with mode `u=r`.

## Variables

`irods_s3_cred` defaults to `[]`. Each entry has `name`, `access_key`, and
`secret_key`; `playbooks/README.md` documents the fields.

## Tests

`playbooks/tests/irods_s3_cred.yml` runs on the `consumer_configured_ubuntu`
test host. It checks the directory's ownership and permissions, that the file
`cred-stale` was removed, the ownership of `cred-1` and `cred-2`, and that
`cred-1` starts with `access-1` and `secret-1` on separate lines. Its mode
condition, `not resp.stat.mode != '0400'`, is double-negated, so that check
fails only when the mode is exactly `0400`.

# Citations

[1] `playbooks/irods_s3_cred.yml` — the playbook.
[2] `playbooks/README.md` — `irods_s3_cred` entry fields.
[3] `playbooks/tests/irods_s3_cred.yml` — the test playbook.
