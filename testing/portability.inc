#!/usr/bin/env bash
#
# Helpers that hide the differences between the GNU tools on Linux and the BSD
# tools on macOS. Source this from the scripts that run on the developer's
# machine; the scripts that run inside the containers always have GNU tools.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Resolves a path to an absolute one with all symlinks expanded, like
# `readlink --canonicalize`, which BSD readlink doesn't support.
ds_canonicalize() {
  local target="$1"
  local dir
  local depth=0

  while [ -L "$target" ]; do
    if [ "$depth" -ge 32 ]; then
      printf 'Too many levels of symbolic links in "%s".\n' "$1" >&2
      return 1
    fi

    dir="$(cd -- "$(dirname -- "$target")" && pwd -P)"
    target="$(readlink "$target")"

    case "$target" in
      /*) ;;
      *) target="$dir"/"$target" ;;
    esac

    depth=$(( depth + 1 ))
  done

  dir="$(cd -- "$(dirname -- "$target")" && pwd -P)"
  printf '%s/%s\n' "$dir" "$(basename -- "$target")"
}


# Parses a command line, using long options only where getopt supports them.
# BSD getopt takes neither long options nor `--`, and it needs the unquoted
# "$*" splitting that GNU getopt makes unnecessary.
ds_getopt() {
  local shortOpts="$1"
  local longOpts="$2"
  local name="$3"
  shift 3

  if ds_have_gnu_getopt; then
    getopt --longoptions "$longOpts" --options "$shortOpts" --name "$name" -- "$@"
  else
    #shellcheck disable=SC2048,SC2086
    getopt "$shortOpts" $*
  fi
}


# GNU getopt exits with 4 when asked if it's GNU getopt; BSD getopt rejects the
# option instead.
ds_have_gnu_getopt() {
  getopt --test > /dev/null 2>&1
  [ "$?" -eq 4 ]
}


# Runs docker compose, preferring the v2 plugin. The inventories name
# containers the way v2 does, so a v1 binary would resolve to host names that
# don't exist.
ds_compose() {
  if docker compose version > /dev/null 2>&1; then
    docker compose "$@"
  elif command -v docker-compose > /dev/null; then
    docker-compose "$@"
  else
    printf 'Neither "docker compose" nor "docker-compose" is available.\n' >&2
    printf 'Install the docker compose plugin.\n' >&2
    return 1
  fi
}


# Fails when the shell is too old for the associative arrays and readarray the
# scripts use. macOS ships bash 3.2 as /bin/bash, so a newer one needs to come
# first in PATH.
ds_require_bash() {
  local required="$1"

  if [ "${BASH_VERSINFO[0]}" -lt "$required" ]; then
    printf 'bash %s or later is required, but this is bash %s.\n' \
      "$required" "${BASH_VERSION}" >&2

    return 1
  fi
}
