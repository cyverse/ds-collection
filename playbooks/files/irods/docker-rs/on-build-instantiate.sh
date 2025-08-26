#!/usr/bin/env bash
#
# Usage:
#  on-build-instantiate
#
# This program expands the build time templates.
#
# To allow iRODS to run as a non-root user and still mount volumes, this script
# allows for the ability to run iRODS with as a user from the docker host
# server. To do this, set the environment variable IRODS_HOST_UID to the UID of
# the host user to run iRODS as.
#
# This program expects the following environment variables to be defined.
#
# IRODS_CLERVER_USER  the name of the rodsadmin user representing the resource
#                     server within the zone
# IRODS_DEFAULT_RES   the name of coordinating resource this server will use by
#                     default
# IRODS_HOST_UID      (optional) the UID of the hosting server to run iRODS as
#                     instead of the default user defined in the container
# IRODS_RES_SERVER    the FQDN or address used by the grid to communicate with
#                     this server
# IRODS_STORAGE_RES   the unix file system resource to server
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

set -o errexit -o nounset -o pipefail

main()
{
  jq_in_place \
    "( .host_resolution.host_entries[]    |
       select(.address_type == \"local\") |
       .addresses
     ) |= map(if . == \"_IRODS_RS_CNAME_\" then \"$IRODS_RES_SERVER\" else . end) |
     .zone_user |= \"$IRODS_CLERVER_USER\"" \
    /etc/irods/server_config.json

  jq_in_place \
    ".irods_cwd              |= sub(\"_IRODS_USER_NAME_\"; \"$IRODS_CLERVER_USER\") |
     .irods_default_resource |= \"$IRODS_DEFAULT_RES\" |
     .irods_home             |= sub(\"_IRODS_USER_NAME_\"; \"$IRODS_CLERVER_USER\") |
     .irods_host             |= \"$IRODS_RES_SERVER\" |
     .irods_user_name        |= \"$IRODS_CLERVER_USER\"" \
    /var/lib/irods/.irods/irods_environment.json

  sed --in-place "s/_IRODS_DEFAULT_RESOURCE_/$IRODS_DEFAULT_RES/" /etc/irods/cyverse-env.re

  local hostUID
  if [[ -n "$IRODS_HOST_UID" ]]
  then
    hostUID="$IRODS_HOST_UID"
  else
    hostUID=$(id --user irods)
  fi

  useradd --no-create-home --non-unique \
          --comment 'iRODS Administrator (host user)' \
          --groups irods \
          --home-dir /var/lib/irods \
          --shell /bin/bash \
          --uid "$hostUID" \
          irods-host-user

  mkdir --mode ug+w /irods_vault/"$IRODS_STORAGE_RES"
  chown irods:irods /irods_vault/"$IRODS_STORAGE_RES"
}

jq_in_place()
{
  local filter="$1"
  local file="$2"

  jq "$filter" "$file" | sponge "$file"
  chown irods:irods "$file"
}

main "$@"
