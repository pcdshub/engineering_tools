#!/bin/bash
# Helper script for starting the ssh agent if needed and doing an ssh-add.
# This will let anyone smoothly run github/ssh related scripts without multiple password prompts.
# This script is intended to be sourced.
# Sourcing this script lets ssh-agent set the proper environment variables it needs to run properly.
#
# Expected usage:
#
# source ssh_agent_helper.sh
# trap ssh_agent_helper_cleanup EXIT
HELPER_STARTED_AGENT="NO"
export HELPER_STARTED_AGENT

# Define an exportable helper for cleaning up the SSH agent
ssh_agent_helper_cleanup() {
    if [ "${HELPER_STARTED_AGENT}" = "YES" ] && [ -n "${SSH_AGENT_PID}" ]; then
        echo "Cleaning up SSH agent"
        ssh-agent -k &> /dev/null
        unset HELPER_STARTED_AGENT
        export HELPER_STARTED_AGENT
        export SSH_AGENT_PID
        export SSH_AUTH_SOCK
    fi
}
export ssh_agent_helper_cleanup
# Clean up immediately if something in this script fails
trap ssh_agent_helper_cleanup ERR SIGINT SIGTERM

# SSH agent check: return code is 1 if there are no identities, 2 if cannot connect to agent.
# Only start the agent on return code 2, otherwise we can just add our identify.
# On return code 0 we don't have to do anything, the user already has this set up.
ssh-add -L &> /dev/null
rval=$?
set -e
if [ "$rval" -eq 2 ]; then
    echo "Starting ssh agent"
    eval "$(ssh-agent -s)" &> /dev/null
    HELPER_STARTED_AGENT="YES"
fi
if [ "$rval" -gt 0 ]; then
    echo "Running ssh-add, may prompt for ssh key password:"
    ssh-add
fi
