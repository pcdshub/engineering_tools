#!/bin/bash
#
# Source this script to set shared environment variables and gain access to three shell functions:
# 1. ctrlenv-pathmunge: adds the bin from a bundle, environment, or application to your path at a specific version
# 2. ctrlenv-activate: activates a released pixi environment in the current shell (useful for scripts)
# 3. ctrlenv-shell: activates a released pixi environment in an exitable subshell (useful for interactive use)
# 4. ctrlenv-versions: shows you which versions exist for an environment or application
#
# Defaults are:
# - Always the latest release
# - If unspecified, the latest bundle release is assumed
# - ctrlenv-base is the default environment
#
# Example usage:
# First, source this script
# source ctrlenv_setup.sh
#
# Then, try one of:
#
# Put the latest released bundle bin on your path:
# ctrlenv-pathmunge
# or
# ctrlenv-pathmunge latest-released
#
# Put a specific released bundle bin on your path:
# ctrlenv-pathmunge 2026/05/26_00
#
# Put the default released environment bin on your path:
# ctrlenv-pathmunge ctrlenv-widgets
#
# Put a specific released environment bin at a specific version on your path
# ctrlenv-pathmunge ctrlenv-lucid/v0.1.2
#
# Put a latest version of an app on your path
# ctrlenv-pathmunge pytmc
#
# Put a specific version of an app on your path
# ctrlenv-pathmunge pytmc/v2.20.0
#
# Activate the default environment
# ctrlenv-activate
# or
# ctrlenv-activate ctrlenv-base
#
# Activate the latest version of a specific environment
# ctrlenv-activate ctrlenv-widgets
#
# Activate a specific version of a specific environment
# ctrlenv-activate ctrlenv-lucid/v0.1.2
#
# Any invocation of ctrlenv-activate also works with ctrlenv-shell
# ctrlenv-shell ctrlenv-widgets
#
# Show which versions exist for an environment or application
# ctrlenv-versions ctrlenv-widgets
# ctrlenv-versions pytmc
#

# Local path settings
PYPS_SITE_TOP="${PYPS_SITE_TOP:-/cds/group/pcds/pyps}"
CTRLENV_BUNDLE_TOP="${CTRLENV_BUNDLE_TOP:-"${PYPS_SITE_TOP}"/bundles}"
CTRLENV_ENVS="${PYPS_SITE_TOP}"/pixi
CTRLENV_APPS="${PYPS_SITE_TOP}"/apps
EPICS_SETUP=/cds/group/pcds/setup
EPICS_PROD=/cds/group/pcds/epics
EPICS_DEV=/cds/group/pcds/epics-dev

# Pixi settings depending on whether you have a local mount to use
if [ -d /u1/"${USER}" ]; then
  # local mount: use it for pixi cache
  export PIXI_CACHE_DIR=/u1/"${USER}"/pixi_cache
  export PIXI_CACHE_NETFS_REDIRECT="always"
else
  # no local mount, but weka is way faster than /tmp somehow
  export PIXI_CACHE_NETFS_REDIRECT="never"
fi

# Default settings for qt
# Avoid OpenGL-related crash for remote sessions
# TODO: investigate whether this should be skipped for local desktop cpu/gpu
export QT_XCB_GL_INTEGRATION=none

# Default settings for pydm
export PYDM_CONFIRM_QUIT=0
export PYDM_DEFAULT_PROTOCOL=ca
export PYDM_DESIGNER_ONLINE=1
# TODO: remove hard-coded default stylesheet once pcdswidgets vacuum widgets no longer need it
export PYDM_STYLESHEET="${EPICS_DEV}"/screens/pydm/vacuumscreens/styleSheet/masterStyleSheet.qss
export PYDM_STYLESHEET_INCLUDE_DEFAULT=1
export PYDM_DISPLAYS_PATH="${EPICS_PROD}"/screens/pydm:"${EPICS_DEV}"/screens/pydm

# Default settings for our apps
export HAPPI_CFG="${CTRLENV_APPS}/hutch-python/device_config/happi.cfg"

# Make sure we have pathmunge command
if ! command -v pathmunge >/dev/null 2>&1 ; then
    # Use site-local version if available
    if [ -f "${EPICS_SETUP}"/pathmunge.sh ]; then
        source "${EPICS_SETUP}"/pathmunge.sh
    else
        # Provide simplest version as a backup
        pathmunge () {
            case ":${PATH}:" in
                *:"$1":*)
                    ;;
                *)
                    PATH=$1:$PATH
            esac
        }
    fi
fi

# Pick a backup at command runtime if EPICS_HOST_ARCH is never set
_ctrlenv-arch() {
    if [ -z "${EPICS_HOST_ARCH}" ]; then
        local archstr
        archstr="$(uname -r)"
        if [[ "$archstr" == *"el9"* ]]; then
            echo rhel9-x86_64
        elif [[ "$archstr" == *"el7"* ]]; then
            echo rhel7-x86_64
        else
            echo unknown
        fi
    else
        echo "${EPICS_HOST_ARCH}"
    fi
}

# Workaround for epics-base installs in pixi env breaking central install
# We did something similar in pcds_conda, but put it in each env instead of centrally
# Without this, basic epics utilities break and EPICS_HOST_ARCH is set to
# standard values like linux-x86_64 instead of SLAC disambiguations like rhel9-x86_64,
# which interferes with _ctrlenv-arch and other things
_reset_to_central_epics() {
    local setup_script
    setup_script="${SETUP_SITE_TOP:=/cds/group/pcds/setup}"/epicsenv-cur.sh
    if [ -f "${setup_script}" ]; then
        source "${setup_script}"
        return 0
    else
        echo "Failed to reactivate central EPICS: cannot find ${setup_script}" >&2
        return 1
    fi
}

# Add a ctrlenv bin to your path
ctrlenv-pathmunge() {
    local target
    local arch
    if [ -z "$1" ]; then
        target=latest-released
    else
        target="$1"
    fi
    arch="$(_ctrlenv-arch)"
    for target_dir in "${CTRLENV_BUNDLE_TOP}" "${CTRLENV_ENVS}" "${CTRLENV_APPS}"; do
        if [ -d "${target_dir}/${target}" ]; then
            if [ -d "${target_dir}/${target}/bin/${arch}" ]; then
                pathmunge "${target_dir}/${target}/bin/${arch}"
                return 0
            elif [ -d "${target_dir}/${target}/latest-released/bin/${arch}" ]; then
                pathmunge "${target_dir}/${target}/latest-released/bin/${arch}"
                return 0
            else
                # Error state: let's try to be a little bit helpful
                echo "Found matching area ${target_dir}/${target} but missing ${arch}, version, or latest-released" >&2
                ctrlenv-versions "$1" >&2
                return 1
            fi
        fi
    done
    echo "No matching path or version found for ctrlenv-pathmunge $target" >&2
    return 1
}

# Activate a ctrlenv environment
ctrlenv-activate() {
    local target
    local arch
    local has_central_epics
    local did_source
    if [ -z "$1" ]; then
        target=ctrlenv-base
    else
        target="$1"
    fi
    arch="$(_ctrlenv-arch)"
    if command -v caget >/dev/null 2>&1; then
        has_central_epics=1
    else
        has_central_epics=0
    fi
    did_source=0
    if [ -d "${CTRLENV_ENVS}/${target}" ]; then
        if [ -f "${CTRLENV_ENVS}/${target}/src/${arch}/.pixi/ctrlenv_activate" ]; then
            source "${CTRLENV_ENVS}/${target}/src/${arch}/.pixi/ctrlenv_activate"
            did_source=1
        elif [ -f "${CTRLENV_ENVS}/${target}/latest-released/src/${arch}/.pixi/ctrlenv_activate" ]; then
            source "${CTRLENV_ENVS}/${target}/latest-released/src/${arch}/.pixi/ctrlenv_activate"
            did_source=1
        else
            # Error state: let's try to be a little bit helpful
            echo "Found matching env ${CTRLENV_ENVS}/${target} but missing ${arch}, version, or latest-released" >&2
            ctrlenv-versions "$1" >&2
            return 1
        fi
    fi
    if [ "${did_source}" -eq 1 ]; then
        if [ "${has_central_epics}" -eq 1 ]; then
            _reset_to_central_epics
            return $?
        fi
        return 0
    fi
    echo "No matching env found for ctrlenv-activate $target" >&2
    return 1
}

# Enter an exitable shell with an environment.
# Useful for exploring the pixi environments interactively.
# Simply "exit" to exit the shell and deactivate the env.
# Do not use this in a shell script- it will interrupt your script with a prompt.
# This is functionally similar to the "pixi shell" command, but doesn't require pixi on the path.
ctrlenv-shell() {
    $SHELL -ic "ctrlenv-activate $*; exec $SHELL -i"
}

# Show which versions exist
ctrlenv-versions() {
    local target
    if [ -z "$1" ]; then
        target=ctrlenv-base
    else
        target="$1"
    fi
    for target_dir in "${CTRLENV_ENVS}" "${CTRLENV_APPS}"; do
        if [ -d "${target_dir}/${target}" ]; then
            echo "Showing versions for ${target}, deployed at ${target_dir}/${target}" >&2
            ls -1 "${target_dir}/${target}"
            return 0
        fi
    done
    echo "No matching env or app found for ctrlenv-versions ${target}" >&2
    return 1
}
