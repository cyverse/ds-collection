# Upgrading iRODS

This procedure upgrades a deployed Data Store's iRODS servers to a later release, e.g., from 4.3.1 to
4.3.4. Three playbooks do the work:

* `irods_upgrade.yml` upgrades the native servers, catalog service providers before consumers.
* `irods_resource_container.yml` upgrades the containerized resource servers by rebuilding their
  image.
* `irods_cfg.yml` checks that the configuration is what the collection deploys for the new release.

Every server in a zone should run the same iRODS release, so upgrade all of them in one maintenance
window. iRODS doesn't support downgrading, and the playbooks refuse to do it, so the way back from a
failed upgrade is the backups taken before it.

The commands below run from the collection's root directory on the Ansible control node, and
`$INVENTORY` is the Data Store's inventory.

## What changes from 4.3.1 to 4.3.4

* The catalog schema is the same in both releases, so the providers apply no schema update when
  they start on 4.3.4.
* The installed plugins, including the S3 resource plugin, are upgraded with `irods-server`.
* From 4.3.2 on, there are no NetCDF plugins, so `irods_provision.yml` removes them, and the NetCDF
  microservices are no longer available.
* Each release has its own rule bases in `playbooks/files/irods/etc/irods/<release>/`, which the
  shared rule bases include. 4.3.4's restore the put PEPs that 4.3.1's leave out to avoid a memory
  leak in 4.3.1.

## Before the maintenance window

1. Use a commit of the collection that has the new release's rule bases,
   `playbooks/files/irods/etc/irods/<release>/`. Every playbook that installs or configures iRODS
   fails without them.

1. Test the upgrade in the testing environment. This upgrades a Data Store from 4.3.1 to 4.3.4,
   then runs every test against it.

   ```bash
   testing/test-all --upgrade-from 4.3.1 --irods-version 4.3.4
   ```

1. Check that the Data Store is configured the way this commit of the collection configures the
   current release. `irods_upgrade.yml` installs only the new release's own rule bases, so it
   refuses to run when the shared ones deployed on a server differ from the collection's.

   ```bash
   ansible-playbook --inventory="$INVENTORY" --check --diff playbooks/irods_cfg.yml
   ```

   If it would change anything, run `irods_cfg.yml` without `--check` before the window, while
   `irods_version` is still the current release.

1. Make sure the inventory puts every containerized resource server in the
   `irods_resource_container` group. `irods_upgrade.yml` leaves the servers in that group, and in
   `unmanaged_systems`, alone, and it fails on any other server in `irods` that doesn't have iRODS
   installed.

1. Make sure every iRODS server can reach `packages.irods.org`. The native servers install the new
   release's packages from it, and the containerized resource servers download them while their
   image builds.

## During the maintenance window

1. Stop client access. `proxy_block.yml` terminates every client connection through the proxy and
   blocks new ones, and stopping the WebDAV and SFTP services keeps them from reconnecting to iRODS.

   ```bash
   ansible-playbook --inventory="$INVENTORY" playbooks/proxy_block.yml
   ansible-playbook --inventory="$INVENTORY" playbooks/webdav_stop.yml
   ansible-playbook --inventory="$INVENTORY" playbooks/sftp_stop.yml
   ```

1. Back up the ICAT database, and take a snapshot of each iRODS server. Taking them after client
   access stops keeps clients from changing the data between them. These are the only way back to
   the earlier release, since the playbooks can't downgrade iRODS.

1. Set `irods_version` to the new release for every host in the `irods` group, e.g., in the
   inventory's `group_vars/irods.yml`.

   ```yaml
   irods_version: 4.3.4
   ```

1. Upgrade the native servers.

   ```bash
   ansible-playbook --inventory="$INVENTORY" playbooks/irods_upgrade.yml
   ```

   It stops the consumers and then the providers it upgrades, upgrades their packages, installs the
   release's rule bases, and starts the providers and then the consumers. Its last play reports
   each containerized resource server whose image has an earlier release, or that it couldn't
   check. If it fails, see [If the upgrade fails](#if-the-upgrade-fails).

1. Upgrade the containerized resource servers.

   ```bash
   ansible-playbook --inventory="$INVENTORY" playbooks/irods_resource_container.yml
   ```

   Their image builds with the new release's packages, and the containers restart on it. Building
   takes a few minutes on each server. Until it's done, they run the earlier release against the
   upgraded providers.

1. Check the configuration. With every server on the new release, `irods_cfg.yml` should change
   nothing.

   ```bash
   ansible-playbook --inventory="$INVENTORY" --check --diff playbooks/irods_cfg.yml
   ```

   `irods_cfg.yml` refuses to run while any server, native or containerized, has a release other
   than `irods_version`, so this also shows that every server was upgraded.

1. Check the upgraded servers.

   * On each native server, as the service account, `imiscsvrinfo` reports
     `relVersion=rods4.3.4`.
   * On each containerized resource server, the image has the release.

     ```bash
     sudo docker compose --file=/var/lib/irods/docker-compose.yml exec -T --user=irods irods-rs \
       dpkg-query --show --showformat='${Version}\n' irods-server
     ```

   * A put to and a get from a resource on each resource server work.
   * `iqstat -a` lists the delayed rules that were queued before the upgrade.
   * Each server's iRODS log has no errors from its start.

1. Restore client access.

   ```bash
   ansible-playbook --inventory="$INVENTORY" playbooks/sftp_start.yml
   ansible-playbook --inventory="$INVENTORY" playbooks/webdav_start.yml
   ansible-playbook --inventory="$INVENTORY" playbooks/proxy_unblock.yml
   ```

## If the upgrade fails

A failure on any server stops `irods_upgrade.yml` on all of them. If a server's packages failed to
upgrade, no server is started, so no consumer runs against a provider that wasn't upgraded. Fix the
cause and run `irods_upgrade.yml` again.

Each server the playbook stops keeps the marker file `/var/lib/irods/.irods-upgrade-stopped` until
it has started every one of them. A rerun upgrades and starts the servers with an earlier release,
and the marked servers that are still stopped, so it also starts the ones the failed run had already
upgraded. It removes the marker from a server that was started since, e.g., by hand, without
restarting it, and leaves alone a server without the marker that was stopped for another reason.

If the Data Store can't be brought up on the new release, restore the server snapshots and the ICAT
database backup, and set `irods_version` back to the earlier release. Restoring only the
configuration and the database isn't enough: the new release's packages stay installed, and the
playbooks refuse to run with an `irods_version` earlier than the installed release.
