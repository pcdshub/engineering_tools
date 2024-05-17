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
                 