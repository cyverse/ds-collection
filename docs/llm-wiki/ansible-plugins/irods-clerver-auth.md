---
type: Plugin
title: irods_clerver_auth Module
description: The cyverse.ds.irods_clerver_auth module, which authenticates the iRODS clerver (server-side client) account with iinit unless its existing authentication file already works.
resource: /plugins/modules/irods_clerver_auth.py
tags: [plugin, module, irods, authentication, icommands]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_clerver_auth` initializes the clerver's zone connection to
iRODS. It shells out to the iCommands `iinit` and `ils`, so it needs them
installed on the managed host and runs as whichever user owns the clerver
environment.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `host` | no | `localhost` | FQDN of the iRODS server used for authentication |
| `password` | yes | | The clerver user's password (`no_log`) |

## Behavior

1. It finds the authentication file by parsing `irods_authentication_file` from
   `iinit -l` output, falling back to `$HOME/.irods/.irodsA`.
2. If that file exists and `ils` succeeds, it returns `changed: false`.
3. Otherwise it sets `IRODS_HOST` when `host` isn't `localhost`, pipes the
   password to `iinit`, and returns `changed: true`.

If `iinit` fails, the module fails with its stderr. `RETURN` is empty.

## Usage

Used by [irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md).

## Tests

`plugins/modules/tests/irods_clerver_auth.yml` runs against `irods_catalog` as
`irods`. It checks that the module reports no change when the authentication
file is already valid, and that `ils` works afterward. Tests for a missing
default authentication file and an out-of-date custom file on a remote server
are TODO placeholders. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

One of the module's `EXAMPLES` invokes `irods_clerver_user` instead of
`irods_clerver_auth`.

# Citations

[1] `plugins/modules/irods_clerver_auth.py` — module source and documentation.
[2] `plugins/modules/tests/irods_clerver_auth.yml` — module test playbook.
