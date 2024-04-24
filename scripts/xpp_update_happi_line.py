#!/usr/bin/env python
"""
Updates items in the happi database to reflect the which line XPP is
using (mono line, pink line).

Assumes pcds-conda, and grabs the currently active happi config.
"""

import argparse

import click
import happi
from ophyd import EpicsSignalRO


def main():
    parser = argparse.ArgumentParser(
        prog='xpp_update_happi_line', description=__doc__
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mono", action="store_true",
                       help='Enforce change to mono line')
    group.add_argument("--pink", action="store_true",
                       help='Enforce change to pink line')

    parser.add_argument('--min', dest='min_z', action='store', type=float,
                        default=784, required=False, help='min z range')

    parser.add_argument('--max', dest='max_z', action='store', type=float,
                        default=788, required=False, help='max z range')

    parser.add_argument('--dry-run', action='store_true', dest='dry_run',
                        default=False, required=False,
                        help='run script without saving to database')

    args = parser.parse_args()
    max_z = args.max_z
    min_z = args.min_z

    pink_active = 0
    mono_active = 0
    if args.pink:
        pink_active = 1
    elif args.mono:
        mono_active = 1
    else:
        pink_active = EpicsSignalRO('XPP:INS:POS:01:IN_DI').get()
        mono_active = EpicsSignalRO('XPP:INS:POS:01:OUT_DO').get()

    # get current working config and happi client
    client = happi.client.Client.from_config()
    # grab all possibly relevant results
    l0_results = client.search_range('z', min_z, max_z, input_branches=['L0'],
                                     output_branches=['L0'])
    l2_results = client.search_range('z', min_z, max_z, input_branches=['L2'],
                                     output_branches=['L2'])

    # assess current state
    print(f'Updating XPP mono-pink line devices z=({min_z}, {max_z})...')
    if not pink_active and mono_active:
        print('  Detected mono line active (L2, sharing beam)')
        new_branch = ['L2']
        results = l0_results
        if not l0_results:
            print('xx no devices on L0 branch to transition')
            return
    elif not mono_active and pink_active:
        print('  Detected pink line active (L0, potentially blocking beam)')
        new_branch = ['L0']
        results = l2_results
        if not l2_results:
            print('xx no devices on L2 branch to transition')
            return
    else:
        print('Invalid configuration, aborting.')
        return

    # Print a diagnostic check for user to verify
    print(f'  {len(results)} devices found to be switched to '
          f'the {new_branch} branch')
    print(f'  device names: {[r.item.name for r in results]}')
    # confirm?
    if not click.confirm('\n  proceed with edits to devices?'):
        print('...aborted')
        return

    # replace input and output branches for each and save info to database
    for res in results:
        res.item.input_branches = new_branch
        res.item.output_branches = new_branch
        print(f'  saving {res.item.name}: in-{res.item.input_branches}, '
              f'out-{res.item.output_branches}')
        if args.dry_run:
            print('  dry run, value not saved')
            continue
        res.item.save()

    print('Mode change completed')


if __name__ == '__main__':
    main()
