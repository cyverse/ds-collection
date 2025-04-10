#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2024 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Provides an ansible module for controlling the iRODS server processes."""

import subprocess
from subprocess import CalledProcessError

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: cyverse.ds.irods_ctl

short_description: an ansible module for controlling the iRODS server processes

description: >
  This module is able to change the state of the iRODS server processes using `irodsctl`. It
  supports starting, stopping, restarting, and restarting only if already started.

version_added: "2.16.9"

author: Tony Edgin

options:
  state:
    description: >
      the end state of the iRODS processes. `started` means the process will be started if it wasn't
      already. `stopped` means the process will be stopped if it was running. `restarted` means it
      will be restarted if it was running or started if it wasn't. `restarted_if_running` means it
      will be restarted only if it was already running.
    choices:
      - started
      - stopped
      - restarted
      - restarted_if_running
    required: false
    default: started
  test_log:
    description: >
      Indicates whether or not server log messages should also be written to
      /var/lib/irods/log/test_mode_output.log. This is not applicable when the `state` is set to
      `stopped`. Also, test logging will only be enable if the iRODS server is started or restarted.
    type: bool
    required: false
    default: false
'''

EXAMPLES = r'''
- name: Stop and iRODS server
  irods_ctl:
    state: stopped
'''

_ARG_SPEC = {
    'state': {
        'type': 'str',
        'choices': ['restarted', 'restarted_if_running', 'started', 'stopped'],
        'default': 'started',
    },
    'test_log': {
        'type': 'bool',
        'default': False,
    },
}


def _call_irodsctl(state, test_log=False):
    cmd = "/var/lib/irods/irodsctl"
    if test_log:
        cmd += " --test"
    cmd += f" {state}"

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=True,
            encoding='utf-8')

        return result.stdout.strip()
    except CalledProcessError as e:
        raise RuntimeError(f"iRODS server failed to {state}") from e


def _is_running():
    status = str(_call_irodsctl("status"))
    return "No iRODS servers running" not in status


def _ensure_started(test_log):
    if not _is_running():
        _call_irodsctl("start", test_log)
        return True

    return False


def _ensure_stopped(_):
    if _is_running():
        _call_irodsctl("stop")
        return True

    return False


def _restart(test_log):
    if _is_running():
        _call_irodsctl("restart", test_log)
    else:
        _call_irodsctl("start", test_log)

    return True


def _restart_if_running(test_log):
    try:
        running = _is_running()
    except RuntimeError:
        return False

    if running:
        _call_irodsctl("restart", test_log)
        return True

    return False


def _ensure_state(params):
    return {
        'restarted': _restart,
        'restarted_if_running': _restart_if_running,
        'started': _ensure_started,
        'stopped': _ensure_stopped,
    }[params['state']](params['test_log'])


def main() -> None:
    """This is the entrypoint."""
    module = AnsibleModule(argument_spec=_ARG_SPEC)

    try:
        module.exit_json(params=module.params, changed=_ensure_state(module.params))
    except RuntimeError as e:
        module.fail_json(params=module.params, msg=str(e))


if __name__ == '__main__':
    main()
