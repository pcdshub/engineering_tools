#!/usr/bin/bash

# define usage
usage()
{
cat << EOF
usage: gatherPVAliases [-h] [-d] patt hutch

gathers all record <-> alias associations from a child's ioc.cfg, st.cmd, and
parent ioc.cfg.

positional arguments:
  patt
  hutch

options:
  -h, --help     show this help message and exit
  -d, --dry_run  Forces a dry run for the script. No files are saved.       

EOF
}

# catch improper number of args or asking for help

if [[ ("$#" -lt 2) || ("$1" == "-h") || ("$1" == "--help") ]]; then
    usage
    exit 0
fi

# source into pcds_conda if not currently active

if [[ ($CONDA_SHLVL == 1) ]];then
    if [[ "$(echo $CONDA_PREFIX | grep 'pcds-')" ]];then
        :
    else
        source pcds_conda
    fi
else
    source pcds_conda
fi

# execute python script
#python /cds/group/pcds/.../getPVAliases.py $@

exit
