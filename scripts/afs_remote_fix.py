#!/usr/bin/python3
"""
afs-remote-fix is a script for repointing your afs git remotes towards github.

It will check if you're currently in a git ioc repo with an afs remote as your origin,
switching it to your fork and adding an upstream remote to pcdshub.

An afs remote is a git remote with a path that looks something like this:
/afs/slac.stanford.edu/g/cd/swe/git/repos/package/epics/ioc/common/ims.git

If this path is your origin, after running the script you will instead have:

origin          git@github.com:your-username/ioc-common-ims.git
upstream        git@github.com:pcdshub/ioc-common-ims.git

If the origin is not an afs path, this script will exit without taking any action.

The script will prompt you for your github username, which is not necessarily
the same as your slac username.
"""

import subprocess


def main() -> int:
    origin = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], universal_newlines=True
    ).strip()
    if not origin.startswith("/afs/"):
        print(f"Your origin {origin} is not an afs repo.")
        return 1
    elif "/ioc/" not in origin:
        print(f"Your origin {origin} is not an ioc repo.")
        return 1
    _, ioc_path = origin.split("/ioc/")
    repo_name = f"ioc-{ioc_path.replace('/', '-', 1)}"
    username = input("Please input your github username:\n")
    new_origin = f"git@github.com:{username}/{repo_name}"
    new_upstream = f"git@github.com:pcdshub/{repo_name}"
    print("\nPlanning to set:")
    print(f"origin to {new_origin}")
    print(f"upstream to {new_upstream}")
    confirm = input("Confirm? y/n\n")
    if not confirm.lower().startswith("y"):
        return 1
    subprocess.run(["git", "remote", "set-url", "origin", new_origin])
    subprocess.run(["git", "remote", "add", "upstream", new_upstream])
    subprocess.run(["git", "remote", "-v"])
    return 0


if __name__ == "__main__":
    exit(main())
