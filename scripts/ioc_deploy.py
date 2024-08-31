#!/usr/bin/python3
"""
ioc-deploy is a script for building and deploying ioc tags from github.
It will create a shallow clone of your IOC in the standard release area at the correct path and "make" it.
If the tag directory already exists, the script will exit.
After making the IOC, we'll write-protect all files and all directories that contain built files
(e.g. those that contain files that are not tracked in git).
We'll also write-protect the top-level directory to help indicate completion.

Example command:
"ioc-deploy -n ioc-foo-bar -r R1.0.0"

This will clone the repository to the default ioc directory and run make
using the currently set EPICS environment variables, then apply write protection.

With default settings this will clone

from https://github.com/pcdshub/ioc-foo-bar
to /cds/group/pcds/epics/ioc/foo/bar/R1.0.0

then cd and make and chmod as appropriate.
"""
import argparse
import enum
import logging
import os
import os.path
import stat
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, List, Optional, Tuple

EPICS_SITE_TOP_DEFAULT = "/cds/group/pcds/epics"
GITHUB_ORG_DEFAULT = "pcdshub"

logger = logging.getLogger("ioc-deploy")


if sys.version_info >= (3, 7, 0):
    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class CliArgs:
        """
        Argparse argument types for type checking.
        """

        name: str = ""
        release: str = ""
        ioc_dir: str = ""
        github_org: str = ""
        remove_write_protection: bool = False
        apply_write_protection: bool = False
        path_override: str = ""
        auto_confirm: bool = False
        dry_run: bool = False
        verbose: bool = False
        version: bool = False
else:
    from types import SimpleNamespace as CliArgs


def get_parser() -> argparse.ArgumentParser:
    current_default_target = str(
        Path(os.environ.get("EPICS_SITE_TOP", EPICS_SITE_TOP_DEFAULT)) / "ioc"
    )
    current_default_org = os.environ.get("GITHUB_ORG", GITHUB_ORG_DEFAULT)
    parser = argparse.ArgumentParser(prog="ioc-deploy", description=__doc__)
    parser.add_argument(
        "--version", action="store_true", help="Show version number and exit."
    )
    parser.add_argument(
        "--name",
        "-n",
        action="store",
        default="",
        help="The name of the repository to deploy. This is a required argument. If it does not exist on github, we'll also try prepending with 'ioc-common-'.",
    )
    parser.add_argument(
        "--release",
        "-r",
        action="store",
        default="",
        help="The version of the IOC to deploy. This is a required argument.",
    )
    parser.add_argument(
        "--ioc-dir",
        "-i",
        action="store",
        default=current_default_target,
        help=f"The directory to deploy IOCs in. This defaults to $EPICS_SITE_TOP/ioc, or {EPICS_SITE_TOP_DEFAULT}/ioc if the environment variable is not set. With your current environment variables, this defaults to {current_default_target}.",
    )
    parser.add_argument(
        "--github_org",
        "--org",
        action="store",
        default=current_default_org,
        help=f"The github org to deploy IOCs from. This defaults to $GITHUB_ORG, or {GITHUB_ORG_DEFAULT} if the environment variable is not set. With your current environment variables, this defaults to {current_default_org}.",
    )
    parser.add_argument(
        "--remove-write-protection",
        action="store_true",
        help="If provided, instead of doing a release, we will remove write protection from an existing release. Incompatible with --apply-write-protection."
    )
    parser.add_argument(
        "--apply-write-protection",
        action="store_true",
        help="If provided, instead of doing a release, we will add write protection to an existing release. Incompatible with --remove-write-protection."
    )
    parser.add_argument(
        "--path-override",
        action="store",
        help="If provided, ignore all normal path-selection rules in favor of the specific provided path. This will let you deploy IOCs or apply protection rules to arbitrary specific paths.",
    )
    parser.add_argument(
        "--auto-confirm",
        "--confirm",
        "--yes",
        "-y",
        action="store_true",
        help="Skip the confirmation promps, automatically saying yes to each one.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not deploy anything, just print what would have been done.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        "--debug",
        action="store_true",
        help="Display additional debug information.",
    )
    return parser


class ReturnCode(enum.IntEnum):
    SUCCESS = 0
    EXCEPTION = 1
    NO_CONFIRM = 2


def main_deploy(args: CliArgs) -> int:
    """
    All main steps of the deploy script.

    This will be called when args has neither of apply_write_protection and remove_write_protection

    Will either return an int return code or raise.
    """
    logger.info("Running ioc-deploy: checking inputs")
    if not (args.name and args.release):
        logger.error("Must provide both --name and --release. Check ioc-deploy --help for usage.")
        return ReturnCode.EXCEPTION

    deploy_dir, upd_name, upd_rel = pick_deploy_dir(args)

    if upd_name is None or upd_rel is None:
        logger.error(f"Something went wrong at package/tag normalization: package {upd_name} at version {upd_rel}")
        return ReturnCode.EXCEPTION

    logger.info(f"Deploying {args.github_org}/{upd_name} at {upd_rel} to {deploy_dir}")
    if Path(deploy_dir).exists():
        raise RuntimeError(f"Deploy directory {deploy_dir} already exists! Aborting.")
    if not args.auto_confirm:
        user_text = input("Confirm release source and target? y/n\n")
        if not user_text.strip().lower().startswith("y"):
            return ReturnCode.NO_CONFIRM
    logger.info(f"Cloning IOC to {deploy_dir}")
    rval = clone_repo_tag(
        name=upd_name,
        github_org=args.github_org,
        release=upd_rel,
        deploy_dir=deploy_dir,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    if rval != ReturnCode.SUCCESS:
        logger.error(f"Nonzero return value {rval} from git clone")
        return rval

    logger.info(f"Building IOC at {deploy_dir}")
    rval = make_in(deploy_dir=deploy_dir, dry_run=args.dry_run)
    if rval != ReturnCode.SUCCESS:
        logger.error(f"Nonzero return value {rval} from make")
        return rval
    logger.info(f"Applying write protection to {deploy_dir}")
    rval = set_permissions(deploy_dir=deploy_dir, protect=True, dry_run=args.dry_run)
    if rval != ReturnCode.SUCCESS:
        logger.error(f"Nonzero return value {rval} from set_permissions")
        return rval
    logger.info("ioc-deploy complete!")
    return ReturnCode.SUCCESS


def main_perms(args: CliArgs) -> int:
    """
    All main steps of the only-apply-permissions script.

    This will be called when args has at least one of apply_write_protection and remove_write_protection

    Will either return an int code or raise.
    """
    logger.info("Running ioc-deploy write protection change: checking inputs")
    if args.apply_write_protection and args.remove_write_protection:
        logger.error("Must provide at most one of --apply-write-protection and --remove-write-protection")
        return ReturnCode.EXCEPTION

    deploy_dir, _, _ = pick_deploy_dir(args)

    rval = None
    if args.apply_write_protection:
        logger.info(f"Applying write protection to {deploy_dir}")
        if not args.auto_confirm:
            user_text = input("Confirm target? y/n\n")
            if not user_text.strip().lower().startswith("y"):
                return ReturnCode.NO_CONFIRM
        rval = set_permissions(deploy_dir=deploy_dir, protect=True, dry_run=args.dry_run)
    elif args.remove_write_protection:
        logger.info(f"Removing write protection from {deploy_dir}")
        if not args.auto_confirm:
            user_text = input("Confirm target? y/n\n")
            if not user_text.strip().lower().startswith("y"):
                return ReturnCode.NO_CONFIRM
        rval = set_permissions(deploy_dir=deploy_dir, protect=False, dry_run=args.dry_run)

    if rval == ReturnCode.SUCCESS:
        logger.info("Write protection change complete!")
    elif rval is None:
        logger.error("Invalid codepath, how did you get here? Submit a bug report please.")
        return ReturnCode.EXCEPTION

    return rval


def pick_deploy_dir(args: CliArgs) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Normalize user inputs and figure out where to deploy to.

    Returns a tuple of three elements:
    - The deploy dir
    - A normalized package name if applicable, or None
    - A normalized tag name if applicable, or None
    """
    if args.name and args.github_org:
        upd_name = finalize_name(
            name=args.name, github_org=args.github_org, verbose=args.verbose
        )
    else:
        upd_name = None
    if upd_name and args.github_org and args.release:
        upd_rel = finalize_tag(
            name=upd_name,
            github_org=args.github_org,
            release=args.release,
            verbose=args.verbose,
        )
    else:
        upd_rel = None
    if args.path_override:
        deploy_dir = args.path_override
    else:
        deploy_dir = get_target_dir(name=upd_name, ioc_dir=args.ioc_dir, release=upd_rel)

    return deploy_dir, upd_name, upd_rel


def finalize_name(name: str, github_org: str, verbose: bool) -> str:
    """
    Check if name is present in org and is well-formed.

    If the name is present, return it.
    If the name is not present and the correct name can be guessed, guess.
    If the name is not present and cannot be guessed, raise.

    A name is well-formed if it starts with "ioc", is hyphen-delimited,
    and has at least three sections.

    For example, "ioc-common-gigECam" is a well-formed name for the purposes
    of an IOC deployment. "ads-ioc" and "pcdsdevices" are not.

    However, "ads-ioc" will resolve to "ioc-common-ads-ioc".
    Only common IOCs will be automatically discovered using this method.
    """
    split_name = name.split("-")
    if len(split_name) < 3 or split_name[0] != "ioc":
        new_name = f"ioc-common-{name}"
        logger.warning(f"{name} is not an ioc name, trying {new_name}")
        name = new_name
    logger.debug(f"Checking for {name} in org {github_org}")
    with TemporaryDirectory() as tmpdir:
        try:
            _clone(
                name=name, github_org=github_org, working_dir=tmpdir, verbose=verbose
            )
        except subprocess.CalledProcessError as exc:
            raise ValueError(
                f"Error cloning repo, make sure {name} exists in {github_org} and check your permissions!"
            ) from exc
    return name


def finalize_tag(name: str, github_org: str, release: str, verbose: bool) -> str:
    """
    Check if release is present in the org.

    We'll try a few prefix options in case the user has a typo.
    In order of priority with no repeats:
    - user's input
    - R1.0.0
    - v1.0.0
    - 1.0.0
    """
    try_release = [release]
    if release.startswith("R"):
        try_release.extend([f"v{release[1:]}", f"{release[1:]}"])
    elif release.startswith("v"):
        try_release.extend([f"R{release[1:]}", f"{release[1:]}"])
    elif release[0].isalpha():
        try_release.extend([f"R{release[1:]}", f"v{release[1:]}", f"{release[1:]}"])
    else:
        try_release.extend([f"R{release}", f"v{release}"])

    with TemporaryDirectory() as tmpdir:
        for rel in try_release:
            logger.debug(f"Checking for release {rel} in {github_org}/{name}")
            try:
                _clone(
                    name=name,
                    github_org=github_org,
                    release=rel,
                    working_dir=tmpdir,
                    target_dir=rel,
                    verbose=verbose,
                )
            except subprocess.CalledProcessError:
                logger.warning(f"Did not find release {rel} in {github_org}/{name}")
            else:
                logger.info(f"Release {rel} exists in {github_org}/{name}")
                return rel
    raise ValueError(f"Unable to find {release} in {github_org}/{name}")


def get_target_dir(name: str, ioc_dir: str, release: str) -> str:
    """
    Return the directory we'll deploy the IOC in.

    This will look something like:
    /cds/group/pcds/epics/ioc/common/gigECam/R1.0.0
    """
    split_name = name.split("-")
    return str(Path(ioc_dir) / split_name[1] / "-".join(split_name[2:]) / release)


def clone_repo_tag(
    name: str,
    github_org: str,
    release: str,
    deploy_dir: str,
    dry_run: bool,
    verbose: bool,
) -> int:
    """
    Create a shallow clone of the git repository in the correct location.
    """
    # Make sure the parent dir exists
    parent_dir = Path(deploy_dir).resolve().parent
    if dry_run:
        logger.info(f"Dry-run: make {parent_dir} if not existing.")
    else:
        logger.debug(f"Ensure {parent_dir} exists")
        parent_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.debug("Dry-run: skip git clone")
        return ReturnCode.SUCCESS
    else:
        return _clone(
            name=name,
            github_org=github_org,
            release=release,
            target_dir=deploy_dir,
            verbose=verbose,
        ).returncode


def make_in(deploy_dir: str, dry_run: bool) -> int:
    """
    Shell out to make in the deploy dir
    """
    if dry_run:
        logger.info(f"Dry-run: skipping make in {deploy_dir}")
        return ReturnCode.SUCCESS
    else:
        return subprocess.run(["make"], cwd=deploy_dir).returncode


def set_permissions(deploy_dir: str, protect: bool, dry_run: bool) -> int:
    """
    Apply or remove write protection from a deploy repo.

    You may or may not have permissions to do this to releases created by other users.

    Applying write protection (protect=True) involves removing the "w" permissions
    from all files, and from directories that contain untracked files.
    We will also remove permissions from the top-level direcotry.

    Removing write protection (protect=False) involves adding "w" permissions
    for the owner and for the group. "w" permissions will never be added for other users.
    We will also add write permissions to the top-level directory.
    """
    if dry_run and not os.path.isdir(deploy_dir):
        # Dry run has nothing to do if we didn't build the dir
        # Most things past this point will error out
        logger.info("Dry-run: skipping permission changes on never-made directory")
        return ReturnCode.SUCCESS

    # Ignore these directories
    exclude = (".git",)

    if not protect:
        # Lazy and simple: chmod everything
        perms = get_add_write_rule(os.stat(deploy_dir, follow_symlinks=False).st_mode)
        if dry_run:
            logger.info(f"Dry-run: skipping chmod({deploy_dir}, {oct(perms)})")
        else:
            os.chmod(deploy_dir, perms)
        for dirpath, dirnames, filenames in exclude_walk(deploy_dir, exclude=exclude):
            for name in dirnames + filenames:
                full_path = os.path.join(dirpath, name)
                perms = get_add_write_rule(os.stat(full_path, follow_symlinks=False).st_mode)
                if dry_run:
                    logger.debug(f"Dry-run: skipping chmod({full_path}, {oct(perms)})")
                else:
                    logger.debug(f"chmod({full_path}, {oct(perms)})")
                    os.chmod(full_path, perms)
        return ReturnCode.SUCCESS

    # Compare the files that exist to the files that are tracked by git
    try:
        ls_files_output = subprocess.check_output(
            ["git", "-C", deploy_dir, "ls-files"],
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    deploy_path = Path(deploy_dir)
    tracked_paths = [deploy_path / subpath.strip() for subpath in ls_files_output.splitlines()]
    build_dir_paths = set()

    def accumulate_subpaths(subpath: Path):
        for path in subpath.iterdir():
            if path.is_symlink():
                continue
            elif path.name in exclude:
                continue
            elif path.is_dir():
                accumulate_subpaths(path)
            elif path.is_file():
                if path not in tracked_paths:
                    build_dir_paths.add(str(path.parent))

    accumulate_subpaths(deploy_path)
    logger.debug(f"Discovered build dir paths {build_dir_paths}")

    # Follow the write protection rules from the docstring
    perms = get_remove_write_rule(os.stat(deploy_dir, follow_symlinks=False).st_mode)
    if dry_run:
        logger.info(f"Dry-run: skipping chmod({deploy_dir}, {oct(perms)})")
    else:
        os.chmod(deploy_dir, perms)
    for dirpath, dirnames, filenames in exclude_walk(deploy_dir, exclude=exclude):
        for dirn in dirnames:
            full_path = os.path.join(dirpath, dirn)
            if full_path in build_dir_paths:
                perms = get_remove_write_rule(os.stat(full_path, follow_symlinks=False).st_mode)
                if dry_run:
                    logger.debug(f"Dry-run: skipping chmod({full_path}, {oct(perms)})")
                else:
                    logger.debug(f"chmod({full_path}, {oct(perms)})")
                    os.chmod(full_path, perms)
            else:
                logger.debug(f"Skip directory perms on {full_path}, not in build dir paths")
        for filn in filenames:
            full_path = os.path.join(dirpath, filn)
            perms = get_remove_write_rule(os.stat(full_path, follow_symlinks=False).st_mode)
            if dry_run:
                logger.debug(f"Dry-run: skipping chmod({full_path}, {oct(perms)})")
            else:
                logger.debug(f"chmod({full_path}, {oct(perms)})")
                os.chmod(full_path, perms)

    return ReturnCode.SUCCESS


def exclude_walk(top_dir: str, exclude: Iterator[str]) -> Iterator[Tuple[str, List[str], List[str]]]:
    """
    Walk through a directory tree with os.walk but exclude some subdirectories.
    """
    for dirpath, dirnames, filenames in os.walk(top_dir):
        for ecl in exclude:
            try:
                dirnames.remove(ecl)
            except ValueError:
                ...
            try:
                filenames.remove(ecl)
            except ValueError:
                ...
        yield dirpath, dirnames, filenames


def get_remove_write_rule(perms: int) -> int:
    """
    Given some existing file permissions, return the same permissions with no writes permitted.
    """
    return perms & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)


def get_add_write_rule(perms: int) -> int:
    """
    Given some existing file permissions, return the same permissions with user and group writes permitted.
    """
    return perms | stat.S_IWUSR | stat.S_IWGRP


def get_version() -> str:
    """
    Determine what version of engineering_tools is being used
    """
    # Possibility 1: git clone (yours)
    try:
        return subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parent), "describe", "--tags"],
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError:
        ...
    # Possibility 2: release dir (someone elses)
    ver = str(Path(__file__).resolve().parent.parent.stem)
    if ver.startswith("R"):
        return ver
    else:
        # We tried our best
        return "unknown.dev"


def _clone(
    name: str,
    github_org: str,
    release: str = "",
    working_dir: str = "",
    target_dir: str = "",
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """
    Clone the repo or raise a subprocess.CalledProcessError
    """
    cmd = ["git", "clone", f"git@github.com:{github_org}/{name}", "--depth", "1"]
    if release:
        cmd.extend(["-b", release])
    if target_dir:
        cmd.append(target_dir)
    kwds = {"check": True}
    if working_dir:
        kwds["cwd"] = working_dir
    if not verbose:
        kwds["stdout"] = subprocess.PIPE
        kwds["stderr"] = subprocess.PIPE
    logger.debug(f"Calling '{' '.join(cmd)}' with kwargs {kwds}")
    return subprocess.run(cmd, **kwds)


def _main() -> int:
    """
    Thin wrapper of main() for log setup, args handling, and high-level error handling.
    """
    args = CliArgs(**vars(get_parser().parse_args()))
    if args.verbose:
        level = logging.DEBUG
        fmt = "%(levelname)-8s %(name)s:%(lineno)d: %(message)s"
    else:
        level = logging.INFO
        fmt = "%(levelname)-8s %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt)
    logger.debug(f"args are {args}")
    try:
        if args.version:
            print(get_version())
            return ReturnCode.SUCCESS
        if args.apply_write_protection or args.remove_write_protection:
            return main_perms(args)
        else:
            return main_deploy(args)
    except Exception as exc:
        logger.error(exc)
        logger.debug("Traceback", exc_info=True)
        return ReturnCode.EXCEPTION


if __name__ == "__main__":
    exit(_main())
