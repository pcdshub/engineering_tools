#!/usr/bin/env python3
"""
Enforce more checks and controls for running the DAQ.
"""

import argparse

from daq_utils import DaqManager


def restartdaq(daqmgr, args):
    daqmgr.restartdaq()


def wheredaq(daqmgr, args):
    daqmgr.wheredaq()


def stopdaq(daqmgr, args):
    daqmgr.stopdaq()


def isdaqmgr(daqmgr, args):
    daqmgr.isdaqmgr()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="run_daq_utils", description=__doc__)

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Report each step: env loaded, cnf used, checks passed.",
    )
    parser.add_argument(
        "--daq",
        action="store_true",
        help="Act on the daq only. Default is both the daq and ami.",
    )
    parser.add_argument(
        "--ami",
        action="store_true",
        help="Act on ami only. Default is both the daq and ami.",
    )
    parser.add_argument(
        "--daq-cnf",
        default=None,
        help="Use this instead of <hutch>_daq.py.",
    )
    parser.add_argument(
        "--ami-cnf",
        default=None,
        help="Use this instead of <hutch>_ami.py.",
    )
    subparsers = parser.add_subparsers()
    psr_restart = subparsers.add_parser(
        "restartdaq",
        help="Verify requirements for running the daq then stop and start it.",
    )
    psr_restart.set_defaults(func=restartdaq)

    psr_where = subparsers.add_parser(
        "wheredaq",
        help="Discover what host is running the daq in the current hutch, if any.",
    )
    psr_where.set_defaults(func=wheredaq)

    psr_stop = subparsers.add_parser(
        "stopdaq", help="Stop the daq in the current hutch."
    )
    psr_stop.set_defaults(func=stopdaq)

    psr_isdaqmgr = subparsers.add_parser(
        "isdaqmgr", help="Determine if the current hutch uses daqmgr"
    )
    psr_isdaqmgr.set_defaults(func=isdaqmgr)

    args = parser.parse_args()

    daqmgr = DaqManager(
        args.verbose, args.daq, args.ami, args.daq_cnf, args.ami_cnf
    )
    args.func(daqmgr, args)
