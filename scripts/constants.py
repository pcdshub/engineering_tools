# -*- coding: utf-8 -*-
"""
Constants used in grep_more_ioc and getPVAliases
"""
###############################################################################
# %% Imports
###############################################################################

import glob as gb

###############################################################################
# %% Constants
###############################################################################

# Check the directories for the iocmanager config file
VALID_HUTCH = sorted([d for d in gb.glob('/cds/group/pcds/pyps/config'
                                         + '/*/')
                      if gb.glob(d + 'iocmanager.cfg')])
# Trim to 3 letter hutch code, include 'all' = '*'
VALID_HUTCH = ['all'] + [s.rsplit(r'/', maxsplit=2)[-2] for s in VALID_HUTCH]

# Keys from iocmanager. Found in /cds/group/pcds/config/*/iocmanager/utils.py
# Update this as needed
DEF_IMGR_KEYS = ['procmgr_config', 'hosts', 'dir', 'id', 'cmd',
                 'flags', 'port', 'host', 'disable', 'history',
                 'delay', 'alias', 'hard']

###############################################################################
# %% Classes
###############################################################################


class Fore:
    """ANSI foreground colors (the subset of colorama.Fore used here)"""
    RED = '\033[31m'
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTBLUE_EX = '\033[94m'
    LIGHTMAGENTA_EX = '\033[95m'


class Style:
    RESET_ALL = '\033[0m'
