#!/usr/bin/env python3
"""
Dummy daq-launcher script using DaqManager.
This script demonstrates the DaqManager class that accepts
verbose and configuration file arguments and provides commands.
"""

import argparse
import getpass
import logging
import os
import shutil
import socket
import sys

from daq_utils import DaqManager

# Setup logging for better output management
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def has_slurm():
    slurm_cmds = ["squeue", "sbatch", "scancel"]
    missing = [cmd for cmd in slurm_cmds if not shutil.which(cmd)]
    if missing:
        logging.error("Missing Slurm commands: %s", ", ".join(missing))
        return False
    return True


def run_cmd(daq, cmd, aimhost=None):
    try:
        func = getattr(daq, cmd)
    except AttributeError:
        logging.error("Invalid daq command: %s", cmd)
        return None

    try:
        if cmd == "restartdaq":
            if aimhost:
                logging.debug("Calling DaqManager.restartdaq('%s')", aimhost)
                return func(aimhost)
            else:
                logging.debug("Calling DaqManager.restartdaq() without aimhost")
                return func()
        else:
            logging.debug("Calling DaqManager.%s()", cmd)
            return func()
    except Exception as e:
        logging.error("Error executing daq command '%s': %s", cmd, e)
        return str(e)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dummy daq-launcher wrapper using DaqManager"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument("--cnf", type=str, help="Path to configuration file")
    parser.add_argument(
        "-m",
        "--aimhost",
        type=str,
        default=socket.gethostname(),
        help="Target hostname (only applicable for restartdaq). Default: local hostname",
    )
    parser.add_argument(
        "cmd",
        choices=["restartdaq", "stopdaq", "wheredaq", "isdaqmgr"],
        help="Command to execute",
    )
    return parser.parse_args()


def main():
    if not has_slurm():
        sys.exit(
            "Exiting: Slurm is required for launching daq processes. Please install Slurm and try again."
        )

    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled.")

    if args.cnf:
        if os.path.isfile(args.cnf):
            logging.debug("Using configuration file: %s", args.cnf)
        else:
            sys.exit(f"Exiting: Configuration file '{args.cnf}' not found.")
    else:
        logging.debug("No configuration file provided. Using default configuration.")

    user = getpass.getuser()
    hostname = socket.gethostname()
    logging.debug("Running as %s on %s", user, hostname)

    daq = DaqManager(args.verbose, args.cnf)

    logging.debug("Executing command: %s", args.cmd)
    # For isdaqmgr, the method will exit with the appropriate code.
    run_cmd(daq, args.cmd, aimhost=args.aimhost)
    # For other commands, additional logging can follow if desired.
    # (isdaqmgr will never return here)


if __name__ == "__main__":
    main()
