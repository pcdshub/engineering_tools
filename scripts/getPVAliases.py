# -*- coding: utf-8 -*-
"""
A script for gathering alias associations from an IOC
"""
###############################################################################
# %% Imports
###############################################################################

import argparse
import copy
import os.path
import re
import sys

from colorama import Fore, Style
from prettytable import PrettyTable

from grep_more_ioc import (clean_ansi, find_ioc, find_parent_ioc, fix_dir,
                           search_file, simple_prompt)

###############################################################################
# %% Functions
###############################################################################


def request_dir(prompt: str,
                default: str = os.getcwd(),) -> str:
    """
    Requests the user for a destination to save a file.

    Parameters
    ----------
    prompt: str
        Prompt to show the user
    default: str
        File destination to default to.
        Default is '{current_dir}'
    Returns
    -------
    str
        Path to file destination.
    """
    while True:
        p = input(prompt+f'(default = {default}): ')
        # Check for default
        if p in ['']:
            result = default
        else:
            result = p
        confirm = simple_prompt('Is '
                                + Fore.LIGHTYELLOW_EX + f'{result} '
                                + Style.RESET_ALL
                                + 'correct? (y/N): ')
        if confirm is True:
            break
    return result


def build_table(input_data: list[dict], columns: list[str] = None,
                **kwargs) -> PrettyTable:
    """
    Build a prettytable from a list of dicts/JSON.
    input_data must be a list(dict)
    Parameters
    ----------
    input_data: list[dict]
        The data to generate a PrettyTable from.
    columns: list, optional
        Columns for the PrettyTable headers. The default is None.
    **kwargs:
        kwargs to pass tohe PrettyTable() for extra customization.

    Returns
    -------
    PrettyTable
        PrettyTable object ready for terminal printing.

    """

    if columns is None:
        col_list = []
    # First get all unique key values from the dict
        for _d in input_data:
            col_list.extend(list(_d.keys()))
        cols = sorted(list(set(col_list)))
    else:
        cols = columns
    # initialize the table
    _tbl = PrettyTable()
    # add the headers
    for c in cols:
        _tbl.add_column(c, [], **kwargs)
    # add the data, strip ANSI color from color headers if any
    for _d in input_data:
        _tbl.add_row([_d.get(clean_ansi(c), '') for c in cols])
    return _tbl


def acquire_aliases(dir_path: str, ioc: str) -> list[dict]:
    """
    Scans the st.cmd of the child IOC for the main PV aliases.
    Returns a list of dicts for the associations. This is the
    top level PV name.
    E.g. LM1K2:MCS2:01:m1 <--> LM2K2:INJ_MP1_MR1

    Parameters
    ----------
    dir_path : str
        Path to the child IOC's release.
    ioc : str
        Child IOC's cfg file name.

    Returns
    -------
    list[dict]
        List of dicts for record <--> alias associations.

    """
    _d = fix_dir(dir_path)
    _f = f'{_d}build/iocBoot/{ioc}/st.cmd'
    if os.path.exists(_f) is False:
        print(f'{_f} does not exist')
        return ''
    search_result = search_file(file=_f, patt=r'db/alias.db')
    _temp = re.findall(r'"RECORD=.*"', search_result)
    output = [re.sub(r'\"|\)|RECORD\=|ALIAS\=', '', s).split(',')
              for s in _temp]
    return [{'record': s[0], 'alias': s[-1]} for s in output]


def process_alias_template(parent_release: str, record: str,
                           alias: str) -> list[str]:
    """
    Opens the parent db/alias.db file and processes the
    substitutions.
    This is the second level of PV names (like in motor records).
    E.g. LM1K2:MCS2:01:m1 <--> LM1K2:INJ_MP1_MR1.RBV

    Parameters
    ----------
    parent_release : str
        Path to the parent IOC's release.
    record : str
        The EPICS record for substitution to generate PV names.
    alias : str
        The alias for the EPICS record.

    Returns
    -------
    list[str]
        DESCRIPTION.

    """

    _target_file = f'{parent_release}/db/alias.db'
    if os.path.exists(_target_file):
        with open(_target_file, encoding='utf-8') as _f:
            _temp = _f.read()
    else:
        print(f'{parent_release} does not exist')
        return None
    # remove the 'alias' prefix from the tuple
    _temp = re.sub(r'alias\(| +', '', _temp)
    _temp = re.sub(r'\)\s*\n', '\n', _temp)
    # then make the substitutions
    _temp = re.sub(r'\$\(RECORD\)', record, _temp)
    _temp = re.sub(r'\$\(ALIAS\)', alias, _temp)
    return [s.replace('"', '').split(',') for s in _temp.split()]


def show_temp_table(input_data: list, col_list: list):
    """
    Formats the 'disable' column in the find_ioc json output for clarity
    and prints the pretty table to the terminal.
    """
    # color code the disable state for easier comprehensions
    temp = copy.deepcopy(input_data)
    for _d in temp:
        if _d.get('disable') is not None:
            if _d.get('disable') is True:
                _d['disable'] = f'{Fore.LIGHTGREEN_EX}True{Style.RESET_ALL}'
        else:
            _d['disable'] = f'{Fore.RED}False{Style.RESET_ALL}'

    # prompt user for initial confirmation
    print(f'{Fore.LIGHTGREEN_EX}Found the following:{Style.RESET_ALL}')
    print(build_table(temp, col_list))


###############################################################################
# %% Argparser
###############################################################################
# parser obj configuration
parser = argparse.ArgumentParser(
    prog='gatherPVAliases',
    description="gathers all record <-> alias associations from a child's "
                "ioc.cfg, st.cmd, and parent ioc.cfg.",
                epilog='')
# main command arguments
parser.add_argument('patt', type=str)
parser.add_argument('hutch', type=str)
parser.add_argument('-d', '--dry_run', action='store_true',
                    default=False,
                    help="Forces a dry run for the script. "
                    "No files are saved.")

###############################################################################
# %% Main
###############################################################################


def main():
    """
    Main function entry point
    """
    # parse args
    args = parser.parse_args()
    # search ioc_cfg and build the dataset
    data = find_ioc(args.hutch, args.patt)
    if data is None:
        print(f'{Fore.RED}No results found for {Style.RESET_ALL}{args.patt}'
              + f'{Fore.RED} in{Style.RESET_ALL}'
              + f'{args.hutch}')
        sys.exit()

    # find the parent directories
    for _d in data:
        _d['parent_ioc'] = find_parent_ioc(_d['id'], _d['dir'])

    # Hard code the column order for the find_ioc output
    column_list = ['id', 'dir',
                   Fore.LIGHTYELLOW_EX + 'parent_ioc' + Style.RESET_ALL,
                   'host', 'port',
                   Fore.LIGHTBLUE_EX + 'alias' + Style.RESET_ALL,
                   Fore.RED + 'disable' + Style.RESET_ALL]
    if args.hutch == 'all':
        column_list = ['hutch'] + column_list
    show_temp_table(data, column_list)

    ans = simple_prompt('Proceed? (Y/n): ', default='Y')
    # Abort if user gets cold feet
    if ans is False:
        sys.exit()
    print(f'{Fore.RED}Skipping disabled child IOCs{Style.RESET_ALL}')

    # initialize the final output to write to file
    final_output = []

    # iterate through all the child ioc dictionaries
    for _ioc in data:
        if _ioc.get('disable') is not True:
            # first acquire the base alias dictionary
            alias_dicts = acquire_aliases(_ioc['dir'], _ioc['id'])
            # show the record aliases to the user
            print(Fore.LIGHTGREEN_EX
                  + 'The following substitutions were found in the st.cmd:'
                  + Style.RESET_ALL)
            print(build_table(alias_dicts, ['record', 'alias'], align='l'))
            # optional skip for all resulting PV aliases
            save_all = (simple_prompt(
                'Do you want to save all resulting PV aliases? '
                + 'This will append '
                + Fore.LIGHTYELLOW_EX
                + f'{len(alias_dicts)}'
                + Style.RESET_ALL
                + ' record sets (y/N): '))

            # initialize flags
            skip_all = None
            show_pvs = None
            save_data = None

            # initialize a default file directory for dumping aliases
            default_dest = os.getcwd() + '/' + f"{_ioc['id']}_alias"
            # now iterate through the alias dicts for PV alias substitutions
            for i, a in enumerate(alias_dicts):
                # then iterate through all the PVs from root PV
                alias_list = process_alias_template(_ioc['parent_ioc'],
                                                    a['record'], a['alias'])
                # capture output based on 61 char max record name
                _chunk = [f"{al[0]:<61}{al[-1]:<61}" for al in alias_list]
                # Demonstrate PV aliases on first iteration
                if (i == 0) | ((show_pvs is True) & (skip_all is False)):
                    # show output to user, building a temp list of dict first
                    _temp = [{'PV': al[0], 'Alias': al[-1]}
                             for al in alias_list]
                    print(Fore.LIGHTGREEN_EX
                          + 'The following PV aliases are built:'
                          + Style.RESET_ALL)
                    print(build_table(_temp, ['PV', 'Alias'], align='l'))
                    del _temp

                # If doing a dry run, skip this block
                if args.dry_run is False:
                    # Respect the skip flag
                    if skip_all is True:
                        continue
                    # ask user for input
                    if save_all is False:
                        save_data = (simple_prompt(
                            'Would you like to save this PV set? (y/N): '))
                        if save_data is True:
                            # give the user an option to be lazy again
                            save_all = (simple_prompt(
                                        'Would you like to apply this for'
                                        + ' ALL remaining sets? (y/N): '))
                            # Avoid some terminal spam using these flags
                            show_pvs = not save_all
                            skip_all = False
                        if save_data is False:
                            skip_all = (simple_prompt(
                                'Skip all further substitutions? (Y/n): ',
                                default='Y'))
                            # Avoid some terminal spam using this flag
                            show_pvs = not skip_all
                            continue
                else:
                    # Set flags to surpress prompts during dry run
                    save_data = False
                if (save_data or save_all) and (args.dry_run is False):
                    final_output.append('\n'.join(_chunk))
                del _chunk

    # write to file, else do nothing
    if (len(final_output) > 0) & (args.dry_run is False):
        dest = request_dir('Choose base file destination',
                           default_dest)
        # make sure the destination exists and mkdir if it doesn't
        if os.path.exists(dest) is False:
            print(Fore.LIGHTBLUE_EX
                  + f'Making directory: {dest}' + Style.RESET_ALL)
            os.mkdir(dest)
        file_dest = dest + "/record_alias_dump.txt"
        with open(file_dest, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_output))
        default_dest = dest
    del final_output

    sys.exit()


if __name__ == '__main__':
    main()
