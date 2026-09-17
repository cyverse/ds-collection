---
type: Playbook
title: irods_resource_hierarchies.yml
description: Creates the coordinating resource hierarchies listed in irods_resource_hierarchies using the irods_resource_hierarchy module.
resource: /playbooks/irods_resource_hierarchies.yml
tags: [irods, resource-hierarchy, coordinating-resources]
timestamp: 2026-09-17T00:00:00Z
---

`irods_resource_hierarchies.yml` targets `irods_catalog` with
`run_once: true`. From the control node, it passes each entry of
`_irods_resource_hierarchies` to
[irods_resource_hierarchy](/ansible-plugins/irods-resource-hierarchy.md). It
connects to the first catalog provider on the zone port as the clerver
user.

## Variables

`irods_resource_hierarchies` defaults to `[ { "name": "demoResc" } ]` when
unset or empty. The first entry's name also becomes the default for
`irods_default_resource`. `playbooks/README.md` documents the entry format.

## Tests

`playbooks/tests/irods_resource_hierarchies.yml` runs `ilsresc` for
`ingestRes` and `replRes` on a catalog provider as `irods`.

# Citations

[1] `playbooks/irods_resource_hierarchies.yml` — the playbook.
[2] `playbooks/group_vars/all/irods.yml` — variable defaults.
[3] `playbooks/tests/irods_resource_hierarchies.yml` — the test playbook.
