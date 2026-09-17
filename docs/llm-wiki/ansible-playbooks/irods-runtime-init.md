---
type: Playbook
title: irods_runtime_init.yml
description: Performs one-time run-time initialization of an iRODS zone — rodsadmin group, standard collections and UUIDs, anonymous access, housekeeping rule scheduling, and conversion of ds-service users to rodsuser.
resource: /playbooks/irods_runtime_init.yml
tags: [irods, initialization, zone, housekeeping, permissions]
timestamp: 2026-09-17T00:00:00Z
---

`irods_runtime_init.yml` configures the zone's catalog contents after the
catalog provider is running. It is imported at the end of
[irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md).

## Run-time initialization play

This play targets `irods_catalog` with `run_once: true` as the service
account. Most tasks run on the control node against the first catalog
provider, using the clerver credentials and the cyverse.ds iRODS modules.

1. Ensures the `rodsadmin` group exists
   ([irods_group](/ansible-plugins/irods-group.md)) and the clerver user is in
   it ([irods_group_member](/ansible-plugins/irods-group-member.md)).
2. Removes `/<zone>/home/rodsadmin` and `/<zone>/trash/home/rodsadmin`, moves
   `/<zone>/home/public` to `/<zone>/home/shared`
   ([irods_move](/ansible-plugins/irods-move.md)), removes
   `/<zone>/trash/home/public`, and creates
   `/<zone>/home/shared/commons_repo/curated`
   ([irods_collection](/ansible-plugins/irods-collection.md)).
3. Gives the zone, home, shared, trash, and trash home collections, and the
   clerver's home and trash collections, an `ipc_UUID` AVU
   ([irods_avu](/ansible-plugins/irods-avu.md), with a value from the
   [uuid lookup](/ansible-plugins/uuid.md)).
4. Only when `init_rodsadmin_perms` is true (default false): grants
   `rodsadmin` write on the top-level static collections and exclusive
   recursive own on `/<zone>/home` and `/<zone>/trash/home`
   ([irods_permission](/ansible-plugins/irods-permission.md)).
5. Ensures an `anonymous` user with an empty password exists
   ([irods_user](/ansible-plugins/irods-user.md)) and gives it read access to
   the zone, home, shared, and curated collections.
6. Opens an admin session as `_irods_admin_username`, with the auth file
   `/var/lib/irods/.irods/.a-adm`, and runs `irule` for
   `cyverse_housekeeping_rescheduleQuotaUsageUpdate`,
   `cyverse_housekeeping_rescheduleStorageFreeSpaceDetermination`, and
   `cyverse_housekeeping_rescheduleTrashRemoval`. It always runs `iexit -f`
   afterward. Each task reports changed only when the rule says it scheduled
   something.
7. For each user of type `ds-service`, adds the user to `public` and creates
   their home and trash collections with own permission for the user and
   none for the clerver.

## ds-service removal plays

Because of irods/irods issue 8233, `iadmin` can't change a user's type from
`ds-service` to `rodsuser`. So a play on `dbms_primary`, run as `postgres`,
updates `r_user_main` in the `ICAT` database directly (tagged
`non_idempotent`). A final play on `irods_catalog` removes the `ds-service`
user type with [irods_user_type](/ansible-plugins/irods-user-type.md).

## Variables

| Variable | Default |
| --- | --- |
| `irods_zone_name` | `tempZone` |
| `irods_clerver_user` / `irods_clerver_password` | `rods` / `rods` |
| `irods_admin_username` / `irods_admin_password` | the clerver user / password |
| `init_rodsadmin_perms` | unset (treated as `false`) |

`init_rodsadmin_perms` is meant to be passed on the command line
(`-e init_rodsadmin_perms=true`). `playbooks/README.md` warns that
initializing the rodsadmin permissions can take a very long time when many
data objects exist, which is why it's skipped by default.

## Tests

`playbooks/tests/irods_runtime_init.yml` verifies the `rodsadmin` group and
membership, removed and moved collections, UUIDs on the starting
collections, the curated collection, rodsadmin permissions, the anonymous
user and its read access, that the housekeeping rules are scheduled, that the
admin session was exited, that no `ds-service` users remain, and that the
user type is gone.

## Related

- [cyverse_housekeeping rules](/irods-rules/cyverse-housekeeping.md)
- [ICAT DBMS](/components/icat-dbms.md)

# Citations

[1] `playbooks/irods_runtime_init.yml` — the playbook.
[2] `playbooks/group_vars/all/irods.yml` — variable defaults.
[3] `playbooks/tests/irods_runtime_init.yml` — the test playbook.
