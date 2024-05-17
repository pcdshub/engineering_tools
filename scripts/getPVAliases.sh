#!/usr/bin/bash

# execute python script
THIS_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

/cds/group/pcds/pyps/conda/py39/envs/pcds-5.8.2/bin/python "${THIS_DIR}/getPVAliases.py" "$@"
