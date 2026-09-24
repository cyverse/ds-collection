#!/usr/bin/env python3
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""
Measures how much memory an iRODS agent gains while it serves a workload, with
and without a given PEP defined, so that PEP memory leaks can be detected.

It has to run on the server whose agents it measures, as the iRODS service
account, since it reads the agents' memory usage from /proc and rewrites a rule
base file in /etc/irods. It is written for the Python 3.6 on CentOS 7.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

from irods.exception import ResourceDoesNotExist
from irods.keywords import DEST_RESC_NAME_KW, RESC_NAME_KW
from irods.session import iRODSSession

ENV_FILE = os.path.expanduser("~/.irods/irods_environment.json")
SERVER_CONFIG = "/etc/irods/server_config.json"
RULE_LANGUAGE_INSTANCE = "irods_rule_engine_plugin-irods_rule_language-instance"
MIB = 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command")

    setup = commands.add_parser(
        "setup", help="create the resource and register the rule base"
    )
    setup.add_argument("config")

    run = commands.add_parser("run", help="run every case and write the results")
    run.add_argument("config")
    run.add_argument("results")

    summarize = commands.add_parser(
        "summarize", help="compare each case with its control"
    )
    summarize.add_argument("results")
    summarize.add_argument("--threshold-mib", type=float, default=16)

    args = parser.parse_args()
    if args.command == "setup":
        do_setup(load_json(args.config))
    elif args.command == "run":
        do_run(load_json(args.config), args.results)
    elif args.command == "summarize":
        print(summarize_results(load_json(args.results), args.threshold_mib))
    else:
        parser.print_help()
        sys.exit(1)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def do_setup(config):
    """Prints "changed" when iRODS needs a restart to load the rule base."""
    with iRODSSession(irods_env_file=ENV_FILE) as session:
        try:
            session.resources.get(config["resource"])
        except ResourceDoesNotExist:
            session.resources.create(
                config["resource"],
                "unixfilesystem",
                host=config["host"],
                path=config["vault"],
            )

    write_rule_base(config["rule_base"], "")

    server_config = load_json(SERVER_CONFIG)
    for engine in server_config["plugin_configuration"]["rule_engines"]:
        if engine["instance_name"] == RULE_LANGUAGE_INSTANCE:
            rule_bases = engine["plugin_specific_configuration"]["re_rulebase_set"]
            if config["rule_base"] not in rule_bases:
                rule_bases.insert(0, config["rule_base"])
                with open(SERVER_CONFIG, "w") as f:
                    json.dump(server_config, f, indent=4)
                print("changed")
            return

    sys.exit("The iRODS Rule Language rule engine is not configured")


def write_rule_base(name, rules):
    # The rule engine rereads a changed rule base when the next agent starts, so
    # no restart is needed between cases.
    with open("/etc/irods/{}.re".format(name), "w") as f:
        f.write(rules)


def do_run(config, results_path):
    results = []
    try:
        for case in build_cases(config):
            print(
                "Running {name} ({workload}, {size})".format(**case),
                file=sys.stderr,
                flush=True,
            )
            write_rule_base(config["rule_base"], case["rule"])
            case["result"] = measure(config, case)
            results.append(case)
    finally:
        write_rule_base(config["rule_base"], "")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)


def build_cases(config):
    """
    Unless the config's controls is false, puts a control case, with no PEP
    defined, ahead of each workload and size.
    """
    cases = []
    controls = set()
    for pep in config["peps"]:
        for size_name in pep["sizes"]:
            size = config["sizes"][size_name]
            base = {
                "workload": pep["workload"],
                "size": size_name,
                "count": size["count"],
                "bytes_per_op": size["bytes"],
            }
            if (
                config.get("controls", True)
                and (pep["workload"], size_name) not in controls
            ):
                controls.add((pep["workload"], size_name))
                cases.append(dict(base, name="control", rule=""))
            cases.append(dict(base, name=pep["name"], rule=pep["rule"]))
    return cases


def measure(config, case):
    workload = WORKLOADS[case["workload"]](config, case)
    workload.prepare()
    try:
        return sample_agent(workload, config["sample_interval"])
    finally:
        workload.cleanup()


def sample_agent(workload, interval):
    """Runs the workload in a thread, recording the memory of the agents serving it."""
    existing = server_pids()
    failure = []

    def target():
        try:
            workload.run()
        except Exception as e:  # pylint: disable=broad-except
            failure.append(e)

    worker = threading.Thread(target=target)
    start = time.monotonic()
    worker.start()

    # Other clients, like the delay server running replication rules, start
    # agents too, so only agents connected to the workload's client count.
    seen = set()
    serving = set()
    series = {}
    cpu = {}
    while True:
        finished = not worker.is_alive()
        elapsed = round(time.monotonic() - start, 2)
        new = server_pids() - existing
        seen |= new
        client = workload.client_pid()
        if client is not None:
            serving |= connected_to(client, new - serving)
        for pid in serving:
            rss = rss_kib(pid)
            if rss is not None:
                series.setdefault(pid, []).append([elapsed, rss])
                cpu[pid] = cpu_ticks(pid) or cpu.get(pid, 0)
        if finished:
            break
        time.sleep(interval)

    worker.join()
    if failure:
        raise failure[0]
    if not series:
        raise RuntimeError(
            "No agent connected to the workload's client was seen; the workload"
            " probably finished faster than the sample interval or was redirected"
            " to a different server"
        )

    # A client can open more than one connection. The agent that served the
    # workload is the one that used the most CPU.
    pid = max(series, key=lambda p: cpu.get(p, 0))
    samples = series[pid]
    rss = [s[1] for s in samples]
    return {
        "seconds": round(time.monotonic() - start, 2),
        "agents_seen": len(seen),
        "agents_serving": len(series),
        "agent_pid": pid,
        "agent_cpu_ticks": cpu.get(pid, 0),
        "rss_first_kib": rss[0],
        "rss_peak_kib": max(rss),
        "rss_last_kib": rss[-1],
        "samples": samples,
    }


def connected_to(client, candidates):
    """Returns the candidates holding the other end of a client's TCP connections."""
    connections = tcp_connections()
    # A client's other sockets, like Unix domain ones, aren't in the TCP tables.
    peers = {
        (connections[i][1], connections[i][0])
        for i in socket_inodes(client)
        if i in connections
    }
    return {
        pid
        for pid in candidates
        if any(connections.get(i) in peers for i in socket_inodes(pid))
    }


def tcp_connections():
    """Maps socket inodes to their local and remote addresses."""
    connections = {}
    for table in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(table) as f:
                next(f)
                for line in f:
                    fields = line.split()
                    connections[int(fields[9])] = (fields[1], fields[2])
        except OSError:
            pass
    return connections


def socket_inodes(pid):
    """Returns the inodes of a process's open sockets, or none if it has exited."""
    inodes = set()
    fd_dir = "/proc/{}/fd".format(pid)
    try:
        fds = os.listdir(fd_dir)
    except OSError:
        return inodes
    for fd in fds:
        try:
            target = os.readlink(os.path.join(fd_dir, fd))
        except OSError:
            continue
        if target.startswith("socket:["):
            inodes.add(int(target[len("socket:[") : -1]))
    return inodes


def server_pids():
    pids = set()
    for entry in os.listdir("/proc"):
        if entry.isdigit():
            try:
                with open("/proc/{}/comm".format(entry)) as f:
                    if f.read().strip() == "irodsServer":
                        pids.add(int(entry))
            except OSError:
                pass
    return pids


def cpu_ticks(pid):
    """Returns the user and system CPU time of a process, or None if it has exited."""
    try:
        with open("/proc/{}/stat".format(pid)) as f:
            # The command name may contain spaces, so split after its closing paren.
            fields = f.read().rsplit(")", 1)[1].split()
        return int(fields[11]) + int(fields[12])
    except (OSError, IndexError):
        return None


def rss_kib(pid):
    """Returns None for a process that has exited, including a zombie."""
    try:
        with open("/proc/{}/status".format(pid)) as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return None


class Workload:
    def __init__(self, config, case):
        self.config = config
        self.case = case
        self.collection = "{}/{}-{}-{}".format(
            config["collection"], case["name"], case["workload"], case["size"]
        )
        self.chunk = os.urandom(case["bytes_per_op"])

    def prepare(self):
        run_command("imkdir", "-p", self.collection)

    def run(self):
        raise NotImplementedError

    def client_pid(self):
        """Returns the process that connects to iRODS, or None if it hasn't started."""
        return os.getpid()

    def cleanup(self):
        run_command("irm", "-rf", self.collection)


class PutWorkload(Workload):
    """Uploads each file in its own DATA_OBJ_PUT request, over one connection."""

    bulk = False

    def prepare(self):
        super().prepare()
        self.client = None
        self.scratch = tempfile.TemporaryDirectory()
        for i in range(self.case["count"]):
            with open(os.path.join(self.scratch.name, "f{}".format(i)), "wb") as f:
                f.write(self.chunk)

    def run(self):
        command = ["iput", "-r", "-R", self.config["resource"]]
        if self.bulk:
            command.append("-b")
        command += [self.scratch.name, self.collection + "/files"]
        self.client = subprocess.Popen(command, stdout=subprocess.DEVNULL)
        if self.client.wait() != 0:
            raise subprocess.CalledProcessError(self.client.returncode, command)

    def client_pid(self):
        return self.client.pid if self.client else None

    def cleanup(self):
        self.scratch.cleanup()
        super().cleanup()


class BulkPutWorkload(PutWorkload):
    """Uploads the files in BULK_DATA_OBJ_PUT requests, over one connection."""

    bulk = True


class WriteWorkload(Workload):
    """Makes one DATA_OBJ_WRITE request per operation to a single data object."""

    def prepare(self):
        super().prepare()
        self.session = iRODSSession(irods_env_file=ENV_FILE)

    def run(self):
        options = {DEST_RESC_NAME_KW: self.config["resource"]}
        with self.session.data_objects.open(
            self.collection + "/obj", "w", **options
        ) as obj:
            for _ in range(self.case["count"]):
                obj.write(self.chunk)

    def cleanup(self):
        # Ending the session only now keeps the agent alive until the last sample.
        self.session.cleanup()
        super().cleanup()


class ReadWorkload(Workload):
    """Makes one DATA_OBJ_READ request per operation from a single data object."""

    def prepare(self):
        super().prepare()
        # The object is written through its own connection, so its agent has
        # exited before the measured one starts.
        with iRODSSession(irods_env_file=ENV_FILE) as session:
            options = {DEST_RESC_NAME_KW: self.config["resource"]}
            with session.data_objects.open(
                self.collection + "/obj", "w", **options
            ) as obj:
                for _ in range(self.case["count"]):
                    obj.write(self.chunk)
        self.session = iRODSSession(irods_env_file=ENV_FILE)

    def run(self):
        options = {RESC_NAME_KW: self.config["resource"]}
        with self.session.data_objects.open(
            self.collection + "/obj", "r", **options
        ) as obj:
            for _ in range(self.case["count"]):
                obj.read(self.case["bytes_per_op"])

    def cleanup(self):
        self.session.cleanup()
        super().cleanup()


WORKLOADS = {
    "bulk_put": BulkPutWorkload,
    "put": PutWorkload,
    "read": ReadWorkload,
    "write": WriteWorkload,
}


def run_command(*command):
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)


def floor_growth_kib(samples):
    """
    Estimates how much memory the agent retained over the whole run. Transfer
    buffers come and go, so the RSS at any one sample can sit well above what
    the agent retains, but a leak raises the floor. The rate at which the floor
    rises, from the lowest sample in the first quarter to the lowest in the last
    quarter, is extrapolated over the run.
    """
    quarter = max(1, len(samples) // 4)
    first_time, first_rss = min(samples[:quarter], key=lambda s: s[1])
    last_time, last_rss = min(samples[-quarter:], key=lambda s: s[1])
    if last_time <= first_time:
        return last_rss - first_rss
    run_time = samples[-1][0] - samples[0][0]
    return round((last_rss - first_rss) * run_time / (last_time - first_time))


def summarize_results(results, threshold_mib):
    controls = {
        (r["workload"], r["size"]): floor_growth_kib(r["result"]["samples"])
        for r in results
        if r["name"] == "control"
    }
    header = (
        "case",
        "workload",
        "size",
        "ops",
        "MiB moved",
        "growth MiB",
        "control MiB",
        "leak MiB",
        "leak B/op",
        "leak B/MiB",
        "agents serving/seen",
        "flag",
    )
    rows = [header]
    for r in results:
        if r["name"] == "control":
            continue
        growth = floor_growth_kib(r["result"]["samples"])
        # Runs without controls count all growth as leak.
        control = controls.get((r["workload"], r["size"]))
        leak_kib = growth - (control or 0)
        moved_mib = r["count"] * r["bytes_per_op"] / MIB
        rows.append(
            (
                r["name"],
                r["workload"],
                r["size"],
                str(r["count"]),
                "{:.0f}".format(moved_mib),
                "{:.1f}".format(growth / 1024),
                "-" if control is None else "{:.1f}".format(control / 1024),
                "{:.1f}".format(leak_kib / 1024),
                "{:.0f}".format(leak_kib * 1024 / r["count"]),
                "{:.0f}".format(leak_kib * 1024 / moved_mib),
                "{}/{}".format(
                    r["result"].get("agents_serving", "?"), r["result"]["agents_seen"]
                ),
                "LEAK?" if leak_kib / 1024 > threshold_mib else "",
            )
        )
    widths = [max(len(row[i]) for row in rows) for i in range(len(header))]
    # zip's strict parameter needs Python 3.10, and every row has the header's length.
    return "\n".join(
        "  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip()  # noqa: B905
        for row in rows
    )


if __name__ == "__main__":
    main()
