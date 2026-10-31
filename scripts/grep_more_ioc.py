# -*- coding: utf-8 -*-
"""
A tool for enhancing the grep_ioc CLI tool for ECS-Delivery team
"""
###############################################################################
# %% Imports
###############################################################################

import argparse
import glob as gb
import os.path
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import fields
from shutil import get_terminal_size

from constants import VALID_HUTCH, Fore, Style

from iocmanager import config as imgr_config
from iocmanager.config import IOCProc
from iocmanager.epics_paths import get_parent

###############################################################################
# %% Global settings
###############################################################################
# Columns of the IOC table, in display order. 'hutch' is only shown for 'all'
COLUMNS = ['hutch', 'name', 'path', 'parent', 'host', 'port', 'history',
           'alias', 'disable']

# Parent lookups are NFS-latency bound, (un)surprisingly. Cold calls can be long
# but are sped up by a little bit of parallelization
# 2x speed up cost at 4 works, negligible when tested with more
PARENT_WORKERS = 4

###############################################################################
# %% Functions
###############################################################################


def search_file(*, file: str, output: list = None,
                patt: str = None, prefix: str = '',
                result_only: bool = False,
                quiet: bool = False, color_wrap: Fore = None) -> str:
    """
    Searches file for regex match and appends the result to a list,
    then formats back into a str with the prefix prepended.

    Parameters
    ----------
    file: str
        The file to read and search. Encoding must be utf-8
    output: list, optional
        A list to appead your results to. The default is None.
    patt: str, optional
        The regex pattern to search for. The default is None.
    prefix: str, optional
        A str prefix to add to each line. The default is ''.
    result_only: str, optional
        Whether to return only the re.findall result instead of
        the whole line. The default is False.
    color_wrap: Fore, optional
        Color wrapping using Colorama.Fore. The default is None.
    quiet: bool, optional
        Whether to surpress the warning printed to terminal when "file"
        does not exist. The default is False.

    Returns
    -------
    list[str]
        A list of the search results with the prefix prepended.
    """
    if output is None:
        output = []
    color = ''
    reset = ''
    if color_wrap is not None:
        color = color_wrap
        reset = Style.RESET_ALL
    if os.path.isfile(file) is False:
        if not quiet:
            print(f'{file} does not exist')
        return ''
    with open(file, 'r', encoding='utf-8') as _f:
        for line in _f.readlines():
            if re.search(patt, line):
                if result_only:
                    # only output the matches with colors wrapped
                    # make sure to reformat into a single str
                    _temp = ' '.join([color + match + reset
                                     for match in re.findall(patt, line)])
                    output.append(_temp+'\n')
                else:
                    output.append(re.sub(patt, color + r'\g<0>' + reset, line))
        return prefix + prefix.join(output)


@contextmanager
def parents_deferred():
    """
    Stops IOCProc from looking up its `parent` while it is constructed.

    The lookup probes the NFS release directories one IOC at a time, which
    is on the 10 s time scale for all hutches. The `parent` is left empty
    and we just fill it in later with `resolve_parents`.
    """
    original = imgr_config.get_parent
    imgr_config.get_parent = lambda *args, **kwargs: ''
    try:
        yield
    finally:
        imgr_config.get_parent = original


def resolve_parents(procs: list[IOCProc]) -> None:
    """
    Fill in `parent` for each IOCProc, looking them up concurrently.
    """
    def _lookup(proc: IOCProc) -> str:
        try:
            return get_parent(proc.path, proc.name)
        except Exception:
            return ''  # same fallback as IOCProc.__post_init__

    with ThreadPoolExecutor(PARENT_WORKERS) as pool:
        for proc, parent in zip(procs, pool.map(_lookup, procs)):
            proc.parent = parent


def load_procs(*, config: str, hutch: str = None) -> list[IOCProc]:
    """
    Load an iocmanager `cfg` and return its IOCProc instances.

    Must be called inside `parents_deferred()` to skip the slow `parent`
    lookup; use `resolve_parents` to fill it in afterwards.

    Parameters
    ----------
    config : str
        path to the iocmanager.cfg of interest
    hutch : str, optional
        hutch identifier code to add as an attr to each IOCProc found,
        by default None

    Returns
    -------
    list[IOCProc]
        every IOCProc defined in the cfg.
    """
    # First open the iocmanager.cfg, if it exists
    if not (os.path.exists(config) and ('iocmanager.cfg' in config)):
        print(f'{config} does not exist or is otherwise invalid.')
        return []

    procs = list(imgr_config.read_config(config).procs.values())
    if hutch:
        for proc in procs:
            proc.hutch = hutch
    return procs


def filter_procs(procs: list[IOCProc], patt: str) -> list[IOCProc]:
    """
    Return the IOCProcs whose fields, joined together, match the regex `patt`.
    This mimicks `grep`ing the iocmanager.cfg itself and allows for some lazy
    searching and filtering.

    Parameters
    ----------
    procs : list[IOCProc]
    patt : str

    Returns
    -------
    list[IOCProc]
    """
    _patt = re.compile(patt)
    # walk the dataclass fields for the IOCProc
    props = fields(IOCProc)
    return [proc for proc in procs
            if _patt.search(''.join(str(getattr(proc, f.name))
                                    for f in props))]


def print_skip_comments(file: str):
    """Prints contents of a file while ignoring comments"""
    try:
        with open(file, 'r', encoding='utf_8') as _f:
            for line in _f.readlines():
                if not line.strip().startswith('#'):
                    print(line.strip())
    except FileNotFoundError:
        print(f'{Fore.RED}Could not open {Style.RESET_ALL}'
              + f'{file}.'
              + f'{Fore.RED} Does not exist{Style.RESET_ALL}')


def simple_prompt(prompt: str, default: str = 'N'):
    """Simple yes/no prompt which defaults to No"""
    while True:
        p = input(prompt).strip().lower()
        if p in ['']:
            p = default.lower()
        if p[0] == 'y':
            result = True
            break
        if p.lower()[0] == 'n':
            result = False
            break
        print('Invalid Entry. Please choose again.')
    return result


def clean_ansi(text: str = None) -> str:
    """
    Removes ANSI escape sequences from a str, including fg/bg formatting.
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def find_ioc(hutch: str = None, patt: str = None,
             valid_hutch: list[str] = VALID_HUTCH) -> list[IOCProc]:
    """
    A pythonic grep_ioc for gathering IOC details from the cfg file

    Parameters
    ----------
    hutch: str, optional
        3 letter lowercase hutch code. May also include 'all'.
        The default is None.
    patt: str, optional
        Regex pattern to search for. The default is None.
    valid_hutch: list[str], optional
        List of valid hutch codes to use. The default is taken
        from the directories in '/cds/group/pcds/pyps/config'

    Raises
    ------
    ValueError
        Hutch code is invalid or regex pattern is missing.

    Returns
    -------
    list[IOCProc]
        List of IOCProc found in the procmanagers.

    """
    # check hutches
    if (hutch is None) | (hutch not in tuple(valid_hutch)):
        print('Invalid entry. Please choose a valid hutch:\n'
              + ','.join(valid_hutch))
        raise ValueError
    # create file paths
    if hutch in tuple(valid_hutch):
        if hutch == 'all':
            path = gb.glob('/cds/group/pcds/pyps/config/*/iocmanager.cfg')
        else:
            path = [f'/cds/group/pcds/pyps/config/{hutch}/iocmanager.cfg']
    # check patt and generate the regex pattern
    if patt is None:
        print('No regex pattern supplied')
        raise ValueError
    # load every hutch first, then resolve all the parents in one pool
    procs = []
    with parents_deferred():
        for cfg in path:
            _hutch = cfg.rsplit(r'/', maxsplit=2)[-2]
            procs.extend(load_procs(config=cfg, hutch=_hutch))
    resolve_parents(procs)
    result = filter_procs(procs, patt)
    if len(result) == 0:
        print(f'{Fore.RED}No results found for {Style.RESET_ALL}{patt}'
              + f'{Fore.RED} in{Style.RESET_ALL} '
              + f'{hutch}')
        return None

    return result


def fix_dir(dir_path: str) -> str:
    """
    Simple function for repairing the child release IOC path based on
    the ioc_cfg output. Returns the proper dir for the child IOC.cfg file.

    Parameters
    ----------
    dir_path : str
        The path to the child IOC's directory as a str.

    Returns
    -------
    str
        The typo-corrected path as a str.

    """

    # catches the short form path
    if dir_path.startswith('ioc/'):
        output_dir = '/cds/group/pcds/epics/'+dir_path
    # for the rare, old child IOCs that only exist in their parent's release
    elif 'common' in dir_path:
        output_dir = dir_path + '/children'
    # Otherwise fine!
    else:
        output_dir = dir_path
    # Make sure the end of the path is a folder!
    if output_dir[-1] != '/':
        output_dir += '/'
    return output_dir


def find_parent_ioc(file: str, path: str) -> str:
    """
    Searches the child IOC for the parent's release pointer
    Returns the parent's IOC as a str.

    Parameters
    ----------
    file : str, optional
        Child IOC's filename. The default is None.
    path : str, optional
        Path to the IOC. The default is None.

    Returns
    -------
    str
        Path to the parent IOC's release.

    """
    file_dir = fix_dir(path)
    if os.path.exists(f'{file_dir}{file}.cfg') is False:
        return 'Invalid. Child does not exist.'
    parent_ioc_release = search_file(file=f'{file_dir}{file}.cfg',
                                     patt='^RELEASE').strip()
    return parent_ioc_release.rsplit('=', maxsplit=1)[-1]


def format_cell(value: any, max_width: int = 50) -> str:
    """
    Formats a table cell; lists as [a, b], long values are truncated with ...


    Parameters
    ----------
    value : any
        The cell value/text. Coerced to ``str``
    max_width : int, optional
        Max width of the printed cell, by default 50

    Returns
    -------
    str
        The text to print in the cell
    """
    text = f'[{", ".join(value)}]' if isinstance(value, list) else str(value)
    return text if len(text) <= max_width else text[:max_width - 3] + '...'


def print_table(iocs: list[IOCProc], cols: list[str]):
    """
    Prints the IOCProc attributes in `cols` as a right-aligned table with a
    row index. When writing to a terminal, columns that do not fit its width
    are printed as further blocks below, like pandas does (every block but
    the last ends its lines with a backslash). Piped output is a single block
    so nothing is split for grep and friends.

    Parameters
    ----------
    iocs : list[IOCProc]
        List of IOCs in dataclass
    cols : list[str]
        Columns to print in the pseudo data-frame
    """
    cells = [[str(i)] + [format_cell(getattr(ioc, c)) for c in cols]
             for i, ioc in enumerate(iocs)]
    heads = [''] + cols
    widths = [max([len(h)] + [len(row[i]) for row in cells])
              for i, h in enumerate(heads)]
    limit = get_terminal_size().columns if sys.stdout.isatty() else None

    # pack the columns into blocks, leaving room for the ' \' marker
    blocks, used = [[]], widths[0]
    for i in range(1, len(heads)):
        if limit and blocks[-1] and used + 2 + widths[i] > limit - 2:
            blocks.append([])
            used = widths[0]
        blocks[-1].append(i)
        used += 2 + widths[i]

    for n, block in enumerate(blocks):
        if n:
            print()
        for r, row in enumerate([heads] + cells):
            line = row[0].ljust(widths[0]) + ''.join(
                '  ' + row[i].rjust(widths[i]) for i in block)
            more = n < len(blocks) - 1 and r == 0
            print(line + (' \\' if more else ''))

###############################################################################
# %% Arg Parser
###############################################################################


def build_parser():
    """
    Builds the parser & subparsers for the main function
    """
    # parser obj configuration
    parser = argparse.ArgumentParser(
        prog='grep_more_ioc',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Transforms grep_ioc output to json object'
                    + ' and prints as a table',
        epilog='For more information on subcommands, use: '
               'grep_more_ioc . all [subcommand] --help')
    # main command arguments
    parser.add_argument('patt', type=str,
                        help='Regex pattern to match IOCs with. '
                        '\nCan match anything in the IOC procmanager object. '
                        'e.g. "lm2k2" or "mcs2" or "gige"')
    parser.add_argument('hutch', type=str,
                        help='3 letter hutch code. Use "all" to search through'
                        ' all hutches.\n'
                        f'Valid arguments: {", ".join(VALID_HUTCH)}')
    parser.add_argument('-d', '--ignore_disabled',
                        action='store_true',
                        default=False,
                        help='Flag for excluding based'
                        + ' on the "disabled" state.')
    # subparsers
    subparsers = parser.add_subparsers(
        help='Required subcommands after capturing IOC information:')
# --------------------------------------------------------------------------- #
# print subarguments
# --------------------------------------------------------------------------- #
    print_frame = (subparsers
                   .add_parser('print',
                               help='Just a simple print of the dataframe'
                               + ' to the terminal.'))

    print_frame.add_argument('print',
                             action='store_true', default=False)

    print_frame.add_argument('-c', '--skip_comments', action='store_true',
                             default=False,
                             help='Prints the IOC.cfg'
                             + ' file with comments skipped')

    print_frame.add_argument('-l', '--list', type=str,
                             metavar='KEY',
                             help='List the column from the dataframe.'
                             + ' Acceptable keys are: '
                             + '[hutch, name, parent, host, port, disable]')

    print_frame.add_argument('-n', '--no_dataframe',
                             action='store_true', default=False,
                             help='Skip printing the dataframe.')

    print_frame.add_argument('-r', '--release', action='store_true',
                             default=False,
                             help="Adds the parent IOC's"
                             + " release to the dataframe")

    print_frame.add_argument('-s', '--print_dirs', action='store_true',
                             default=False,
                             help='Prints the child & parent IOC'
                             + ' directories as the final output')

    print_frame.add_argument('-y', '--print_history', action='store_true',
                             default=False,
                             help="Prints the child IOC's history to terminal")
# --------------------------------------------------------------------------- #
# search subarguments
# --------------------------------------------------------------------------- #
    search = subparsers.add_parser('search',
                                   help='For using regex-like searches in the'
                                   + ' child IOC.cfg captured by grep_ioc.'
                                   + '\nUseful for quickly gathering instance'
                                   + ' information, IP addr, etc.')

    search.add_argument('search',
                        type=str, help='PATT to use for regex search in file',
                        metavar='PATT')

    search.add_argument('-n', '--no_color', action='store_true',
                        default=False,
                        help="Don't wrap the search results with a color")

    search.add_argument('-o', '--only_results', action='store_true',
                        default=False,
                        help="Only print the results of the regex match. Like"
                        " 'grep -o'.")

    search.add_argument('-O', '--no_filename', action='store_true',
                        default=False,
                        help="Don't print filename before results")

    search.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='Surpresses file warning for paths that do not'
                        + ' exist.')

    search.add_argument('-s', '--only_search', action='store_true',
                        default=False,
                        help="Don't print the dataframe, just search results.")
    return parser

###############################################################################
# %% Main
###############################################################################


def main():
    """
    Main entry point of the program. For using with CLI tools.
    """
    parser = build_parser()
    args = parser.parse_args()
    # read grep_ioc output
    data = find_ioc(args.hutch, args.patt)

    # exit if grep_ioc finds nothing
    if (data is None or len(data) == 0):
        print(f'{Fore.RED}No IOCs were found.\nExiting . . .{Style.RESET_ALL}')
        sys.exit()

    # filter out disabled IOCs if requested
    if args.ignore_disabled is True:
        data = [ioc for ioc in data if not ioc.disable]

    # only show the hutch column if searching all hutches
    cols = [c for c in COLUMNS if c != 'hutch' or args.hutch == 'all']
    names_paths = [(ioc.name, ioc.path) for ioc in data]

# --------------------------------------------------------------------------- #
# %%% print
# --------------------------------------------------------------------------- #
    # print the table
    if hasattr(args, 'print'):
        if not args.release:
            cols.remove('parent')

        if not args.no_dataframe:
            print_table(data, cols)

        if args.skip_comments:
            for ioc, d in names_paths:
                # fixes dirs if ioc_manager truncates the path due to
                # common ioc dir path
                target_dir = fix_dir(d)
                print(f'{Fore.LIGHTBLUE_EX}Now in: {target_dir}'
                      + Style.RESET_ALL)
                print(f'{Fore.LIGHTYELLOW_EX}{ioc}:{Style.RESET_ALL}')
                # prints the contents of the file while ignoring comments
                print_skip_comments(file=f'{target_dir}{ioc}.cfg')

        if args.print_dirs:
            print(f'{Fore.LIGHTBLUE_EX}\nDumping directories:\n'
                  + Style.RESET_ALL)
            for f, d in names_paths:
                search_result = find_parent_ioc(f, d)
                d = fix_dir(d)
                # check for cases where child IOC.cfg DNE
                if not os.path.exists(f'{d}{f}.cfg'):
                    child_ioc = ''
                    color_prefix = Fore.LIGHTRED_EX
                else:
                    child_ioc = f'{f}.cfg'
                    color_prefix = Fore.LIGHTBLUE_EX
                # Print this for easier cd / pushd shenanigans
                print(f'{d}{Fore.LIGHTYELLOW_EX}{child_ioc}{Style.RESET_ALL}'
                      + '\n\t\t|-->'
                      + f'{Fore.LIGHTGREEN_EX}RELEASE={Style.RESET_ALL}'
                      + f'{color_prefix}{search_result}{Style.RESET_ALL}'
                      )

        if args.print_history is True:
            print(f'{Fore.LIGHTMAGENTA_EX}\nDumping histories:\n'
                  + Style.RESET_ALL)
            for ioc in data:
                print(f'{Fore.LIGHTYELLOW_EX}{ioc.name}{Style.RESET_ALL}'
                      + '\nhistory:\n\t'
                      + '\n\t'.join(ioc.history))

        if args.list:
            print('\n'.join(str(getattr(ioc, args.list)) for ioc in data))

# --------------------------------------------------------------------------- #
# %%% search
# --------------------------------------------------------------------------- #
    # do a local grep on each file in their corresponding directory
    if hasattr(args, 'search'):
        # optionally print the table
        if not args.only_search:
            print_table(data, cols)
        check_search = []
        _color = Fore.LIGHTRED_EX
        if args.no_color:
            _color = None
        for ioc, d in names_paths:
            target_dir = fix_dir(d)
            # Search for pattern after moving into the directory
            if args.search is not None:
                search_result = (search_file(file=f'{target_dir}{ioc}.cfg',
                                             patt=args.search,
                                             result_only=args.only_results,
                                             color_wrap=_color,
                                             quiet=args.quiet)
                                 .strip()
                                 )
                if len(search_result) > 0:
                    if not args.no_filename:
                        print(f'{Fore.LIGHTYELLOW_EX}{ioc}:{Style.RESET_ALL}')
                    print(''.join(search_result.strip()))
                    check_search.append(len(search_result))
        if len(check_search) == 0:
            print(Fore.RED + 'No search results found' + Style.RESET_ALL)
# --------------------------------------------------------------------------- #
# %%% Exit
# --------------------------------------------------------------------------- #
    sys.exit()


# --------------------------------------------------------------------------- #
# %%% Entry point
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main()
