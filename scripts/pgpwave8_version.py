import argparse

import setupLibPaths  # noqa: F401
import wave8 as w8

parser = argparse.ArgumentParser()
parser.add_argument(
    "-l",
    type=int,
    required=False,
    default=0,
    help="PGP lane number",
)

parser.add_argument(
    "--dev",
    type=str,
    required=False,
    default="/dev/datadev_0",
    help="PGP device (default /dev/datadev_0)",
)

args = parser.parse_args()

# Set base
wave8Board = w8.Top(
    dev=args.dev,
    lane=args.l,
    promLoad=True,
    pollEn=False,
    initRead=True,
    timeout=5.0,
)

wave8Board.start()
wave8Board.AxiVersion.printStatus()
wave8Board.stop()
