# ansible-plugins

* [irods_avu Module](/ansible-plugins/irods-avu.md) - The cyverse.ds.irods_avu module, which adds, sets, or removes an AVU on an iRODS data object, collection, or resource through python-irodsclient as a rodsadmin user.
* [irods_clerver_auth Module](/ansible-plugins/irods-clerver-auth.md) - The cyverse.ds.irods_clerver_auth module, which authenticates the iRODS clerver (server-side client) account with iinit unless its existing authentication file already works.
* [irods_collection Module](/ansible-plugins/irods-collection.md) - The cyverse.ds.irods_collection module, which creates or force-removes an iRODS collection, optionally creating parent collections, through python-irodsclient.
* [irods_ctl Module](/ansible-plugins/irods-ctl.md) - The cyverse.ds.irods_ctl module, which starts, stops, restarts, or conditionally restarts the iRODS server processes with /var/lib/irods/irodsctl, optionally enabling test-mode logging.
* [irods_group_member Module](/ansible-plugins/irods-group-member.md) - The cyverse.ds.irods_group_member module, which adds users to or removes users from an existing iRODS group through python-irodsclient.
* [irods_group Module](/ansible-plugins/irods-group.md) - The cyverse.ds.irods_group module, which creates or removes an iRODS group through python-irodsclient.
* [irods_move Module](/ansible-plugins/irods-move.md) - The cyverse.ds.irods_move module, which renames an iRODS collection through python-irodsclient and treats an already-completed move as success.
* [irods_permission Module](/ansible-plugins/irods-permission.md) - The cyverse.ds.irods_permission module, which sets or removes a user's null, read, write, or own permission on an iRODS collection or data object, optionally recursing into a collection's members.
* [irods_resource_hierarchy Module](/ansible-plugins/irods-resource-hierarchy.md) - The cyverse.ds.irods_resource_hierarchy module, which creates missing coordinating resources and attaches child resources to build an iRODS resource hierarchy.
* [irods_resource_up Module](/ansible-plugins/irods-resource-up.md) - The cyverse.ds.irods_resource_up module, which sets an iRODS resource's status to up along with the status of every ancestor resource.
* [irods_unixfilesystem_resource Module](/ansible-plugins/irods-unixfilesystem-resource.md) - The cyverse.ds.irods_unixfilesystem_resource module, which creates an iRODS unixfilesystem storage resource and fails if one with the same name exists with a different type, host, vault, or context.
* [irods_user_type Module](/ansible-plugins/irods-user-type.md) - The cyverse.ds.irods_user_type module, which adds or removes an iRODS user type token using iadmin and iquest.
* [irods_user Module](/ansible-plugins/irods-user.md) - The cyverse.ds.irods_user module, which creates, updates (type, info, password), or removes an iRODS user, optionally emptying the user's home and trash before removal.
* [json_patch Module](/ansible-plugins/json-patch.md) - The cyverse.ds.json_patch module, which adds or updates top-level string and number fields in a JSON file on a managed host.
* [port_check_receiver Module](/ansible-plugins/port-check-receiver.md) - The cyverse.ds.port_check_receiver module, which listens on a set of TCP and UDP ports, answers every message with pong, and exits on a stop message, for verifying network routes with port_check_sender.
* [port_check_sender Module](/ansible-plugins/port-check-sender.md) - The cyverse.ds.port_check_sender module, which sends a message to each listed TCP and UDP port on a destination host and fails listing every port that didn't reply.
* [uuid Lookup](/ansible-plugins/uuid.md) - The cyverse.ds.uuid lookup plugin, which returns a version 1, 3, 4, or 5 UUID using Python's uuid module.
* [warn_if_false Test](/ansible-plugins/warn-if-false.md) - The cyverse.ds.warn_if_false Jinja2 test, which returns a Boolean unchanged and prints a warning when it is false; used to gate restart and reboot handlers.
