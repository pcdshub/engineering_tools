#!/bin/bash
#
# Source this script to set shared environment variables and gain access to two shell functions:
# 1. ctrlenv-pathmunge: adds the bin from a bundle, environment, or application to your path at a specific version
# 2. ctrlenv-activate: puts you into a released pixi environment (pixi shell)
#
# Defaults are:
# - Always the latest release
# - If unspecified, the latest bundle release is assumed
# - base is the default environment
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
# ctrlenv-pathmunge base
#
# Put a specific released environment bin at a specific version on your path
# ctrlenv-pathmunge lucid/v0.1.2
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
# ctrlenv-activate base
#
# Activate the latest version of a specific environment
# ctrlenv-activate widgets
#
# Activate a specific version of a specific environment
# ctrlenv-activate lucid/v0.1.2
#

# Local path settings
PYPS_SITE_TOP="${PYPS_SITE_TOP:-/cds/group/pcds/pyps}"
CTRLENV_BUNDLE_TOP="${CTRLENV_BUNDLE_TOP:-"${PYPS_SITE_TOP}"/bundles}"
CTRLENV_ENVS="${PYPS_SITE_TOP}"/pixi
CTRLENV_APPS="${PYPS_SITE_TOP}"/apps
EPICS_SETUP=/cds/group/pcds/setup
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
    # Check bundle first: exact match only
    if [ -d "${CTRLENV_BUNDLE_TOP}/${target}" ]; then
        pathmunge "${CTRLENV_BUNDLE_TOP}/${target}/bin/${arch}"
        return 0
    fi
    # Check envs second: allow omit ctrlenv- prefix
    for tg in "$target" "ctrlenv-${target}"; do
        if [ -d "${CTRLENV_ENVS}/${tg}" ]; then
            if [ -d "${CTRLENV_ENVS}/${tg}/bin/${arch}" ]; then
                pathmunge "${CTRLENV_ENVS}/${tg}/bin/${arch}"
                return 0
            else
            # Wasn't a version- pick latest
                pathmunge "${CTRLENV_ENVS}/${tg}/latest-released/bin/${arch}"
                return 0
            fi
        fi
    done
    # Check apps last
    if [ -d "${CTRLENV_APPS}/${target}" ]; then
        if [ -d "${CTRLENV_APPS}/${target}/bin/${arch}" ]; then
            pathmunge "${CTRLENV_APPS}/${target}/bin/${arch}"
            return 0
        else
        # Wasn't a version- pick latest
            pathmunge "${CTRLENV_APPS}/${target}/latest-released/bin/${arch}"
            return 0
        fi
    fi
    echo "No matching bundle, env, or app found for ctrlenv-pathmunge $1" >&2
    return 1
}


# Activate a ctrlenv environment
ctrlenv-activate() {
    local target
    local arch
    if [ -z "$1" ]; then
        target=base
    else
        target="$1"
    fi
    arch="$(_ctrlenv-arch)"
    # For envs allow omit ctrlenv- prefix
    for tg in "$target" "ctrlenv-${target}"; do
        if [ -d "${CTRLENV_ENVS}/${tg}" ]; then
            if [ -d "${CTRLENV_ENVS}/${tg}/bin/${arch}" ]; then
                pixi shell --manifest-path "${CTRLENV_ENVS}/${tg}/src/${arch}"
                return $?
            else
            # Wasn't a version- pick latest
                pixi shell --manifest-path "${CTRLENV_ENVS}/${tg}/latest-released/src/${arch}"
                return $?
            fi
        fi
    done
    echo "No matching env found for ctrlenv-activate $1" >&2
    return 1
}
