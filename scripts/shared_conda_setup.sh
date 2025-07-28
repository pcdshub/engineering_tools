#!/usr/bin/env bash

# This is sourced by pcds_conda and dev_conda
# It contains the shared lines between those two sourceable scripts
# See pcds_conda and dev_conda

# Filesystem-specific settings
# Change these if we change the filesystem again
PCDS_ROOT="/cds/group/pcds"
SETUP_ROOT="${PCDS_ROOT}/setup"
PYPS_ROOT="${PCDS_ROOT}/pyps"
APPS_ROOT="${PYPS_ROOT}/apps"
CONDA_ROOT="${PYPS_ROOT}/conda"

# Clear externally set paths that may mess with imports etc.
unset LD_LIBRARY_PATH
unset PYTHONPATH

# Pick up EPICS environment variable settings just in case user did not
source "${SETUP_ROOT}/epics-ca-env.sh"

# BASE_ENV transition points
FIRST_PCDS_PY38="4.0.0"
FIRST_PCDS_PY39="4.2.0"
FIRST_PCDS_PY312="6.0.0"

# Helper script for finding your conda environment
version_ge () {
  # Is first version greater than or equal to the second?
  # Assumes no prefix, just numbers, major.minor.bugfix
  first_ver="$1"
  second_ver="$2"
  first_maj="$(echo "${first_ver}" | cut -d . -f 1)"
  first_min="$(echo "${first_ver}" | cut -d . -f 2)"
  first_bug="$(echo "${first_ver}" | cut -d . -f 3)"
  second_maj="$(echo "${second_ver}" | cut -d . -f 1)"
  second_min="$(echo "${second_ver}" | cut -d . -f 2)"
  second_bug="$(echo "${second_ver}" | cut -d . -f 3)"
  if [[ "${first_maj}" -gt "${second_maj}" ]]; then
    return 0
  elif [[ "${first_maj}" -lt "${second_maj}" ]]; then
    return 1
  else
    if [[ "${first_min}" -gt "${second_min}" ]]; then
      return 0
    elif [[ "${first_min}" -lt "${second_min}" ]]; then
      return 1
    else
      if [[ "${first_bug}" -ge "${second_bug}" ]]; then
        return 0
      else
        return 1
      fi
    fi
  fi
}

# Based on the user's selection or non-selection, pick the correct env
if [[ -z "${PCDS_CONDA_VER}" ]]; then
  # If env var unset, then default to latest
  BASE_ENV="${CONDA_ROOT}/py312"
  PYTHON_VER="3.12"
  PCDS_CONDA_VER="$(cat "${BASE_ENV}/latest_env")"
else
  # Figure out which base to use
  if [[ -z "${PCDS_CONDA_VER##*-*}" ]]; then
    # We had a dash, there must be a prefix in the name
    SERIES="$(echo "${PCDS_CONDA_VER}" | cut -d - -f 1)"
    VER_NUM="$(echo "${PCDS_CONDA_VER}" | cut -d - -f 2)"
  else
    # We didn't have a dash or a prefix, assume it is pcds
    SERIES="pcds"
    VER_NUM="${PCDS_CONDA_VER}"
    PCDS_CONDA_VER="pcds-${PCDS_CONDA_VER}"
  fi
  # Figure out where the base environment is
  # Base environment should be updated with every new python version
  # But in practice this can be skipped
  if [[ "${SERIES}" == "pcds" ]]; then
    if version_ge "${VER_NUM}" "${FIRST_PCDS_PY312}"; then
      BASE_ENV="${CONDA_ROOT}/py312"
      PYTHON_VER="3.12"
    elif version_ge "${VER_NUM}" "${FIRST_PCDS_PY39}"; then
      BASE_ENV="${CONDA_ROOT}/py39"
      PYTHON_VER="3.9"
    elif version_ge "${VER_NUM}" "${FIRST_PCDS_PY38}"; then
      BASE_ENV="${CONDA_ROOT}/py36"
      PYTHON_VER="3.8"
    else
      BASE_ENV="${CONDA_ROOT}/py36"
      PYTHON_VER="3.6"
    fi
  else
    BASE_ENV="${CONDA_ROOT}/py39"
    PYTHON_VER="3.9"
  fi
fi

# Setup the conda environment
source "${BASE_ENV}/etc/profile.d/conda.sh"
conda activate "${PCDS_CONDA_VER}"

# Common locations, will be used below
ENV_FILES="${BASE_ENV}/envs/${PCDS_CONDA_VER}"
SITE_PACKAGES="${ENV_FILES}/lib/python${PYTHON_VER}/site-packages"
PCDSDEVICES_PROD_UI="${SITE_PACKAGES}/pcdsdevices/ui"
PCDSDEVICES_DEV_UI="${APPS_ROOT}/dev/pcdsdevices/pcdsdevices/ui"
TYPHOS_PROD_DEVICES_UI="${SITE_PACKAGES}/typhos/ui/devices"
EPICS_DEV="${PCDS_ROOT}/epics-dev"

# Various settings for ui apps
export PYDM_CONFIRM_QUIT=0
export PYDM_DEFAULT_PROTOCOL=ca
export PYDM_DESIGNER_ONLINE=1
# For typhos: check prod folders first, then dev folders if nothing was found
export PYDM_DISPLAYS_PATH="${PCDSDEVICES_PROD_UI}:${TYPHOS_PROD_DEVICES_UI}:${PCDSDEVICES_DEV_UI}:${EPICS_DEV}/screens/pydm:${EPICS_DEV}"
export PYDM_STYLESHEET="${EPICS_DEV}/screens/pydm/vacuumscreens/styleSheet/masterStyleSheet.qss"
export PYDM_STYLESHEET_INCLUDE_DEFAULT=1
export LUCID_CONFIG="${APPS_ROOT}/hutch-python/lucid_config/"
export HAPPI_CFG="${APPS_ROOT}/hutch-python/device_config/happi.cfg"
export TYPHOS_JIRA_EMAIL_SUFFIX="@slac.stanford.edu"

# Keep tokens off of github
TOKEN_DIR="${CONDA_ROOT}/.tokens"
source "${TOKEN_DIR}/typhos.sh"

# Revert to Software Raster when SSH to avoid issues with QtQuick.
# The same was done with PyDM and this fixes Designer and friends.
if [ -n "${SSH_CONNECTION}" ]; then
  export QT_QUICK_BACKEND="software"
fi
