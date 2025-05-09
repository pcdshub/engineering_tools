#!/usr/bin/env python3
"""
daq-launcher script using DaqManager.
This script demonstrates the DaqManager class that accepts
verbose and configuration file arguments and provides commands.
"""

import argparse
import getpass
import logging
import shutil
import socket
import sys

from daq_utils import DAQMGR_HUTCHES, DaqManager, call_subprocess

# Setup logging for better output management
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def check_isdaqmgr():
    """
    Determine if the current hutch uses daqmgr.

    Returns:
        True if the current hutch is in the list of DAQ manager hutches.
        False if it's not.

    Behavior:
        - Uses 'get_info --gethutch' to determine the current hutch.
        - Compares the result to the DAQMGR_HUTCHES list.
        - If this check fails (e.g. get_info is missing or returns an error),
          the function will print an error message to stderr and exit with code 2.

    Exit codes (when called from main()):
        0 => This is a DAQ manager hutch
        1 => Not a DAQ manager hutch
        2 => Unexpected error (e.g., get_info failed)
    """
    try:
        hutch = call_subprocess("get_info", "--gethutch")
        result = hutch in DAQMGR_HUTCHES
        logging.debug("check_isdaqmgr: hutch=%s, result=%s", hutch, result)
        return result
    except Exception as e:
        print(f"[isdaqmgr] Error: Failed to determine hutch: {e}", file=sys.stderr)
        sys.exit(2)


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
    parser.add_argument("-C", "--cnf", type=str, help="Path to configuration file")
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
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled.")

    # Handle `isdaqmgr` first: this command should not depend on SLURM,
    # configuration files, or any external setup beyond `get_info` and `DAQMGR_HUTCHES`.
    if args.cmd == "isdaqmgr":
        if check_isdaqmgr():
            sys.exit(0)
        else:
            sys.exit(1)

    if not has_slurm():
        sys.exit(
            "Exiting: Slurm is required for launching daq processes. Please install Slurm and try again."
        )

    if not args.cnf:
        logging.debug("No configuration file provided. Using default configuration.")

    user = getpass.getuser()
    hostname = socket.gethostname()
    logging.debug("Running as %s on %s", user, hostname)

    daq = DaqManager(args.verbose, args.cnf)

    logging.debug("Executing command: %s", args.cmd)
    run_cmd(daq, args.cmd, aimhost=args.aimhost)


if __name__ == "__main__":
    main()
