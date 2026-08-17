"""
Guides the user through setting up their github ssh keys.
"""

import subprocess
from pathlib import Path
from typing import List

import click
import pexpect

SUPPORTED_KEYS = ['id_rsa.pub', 'id_ecdsa.pub', 'id_ed25519.pub']


def sp_run(args: List[str]) -> subprocess.CompletedProcess:
    """small wrapper to capture stdout, stderr"""
    process = subprocess.run(
        args,
        capture_output=True,
    )

    return process


def ssh_is_enabled() -> bool:
    process = sp_run(['ssh', '-T', 'git@github.com'])

    if "You've successfully authenticated" in process.stderr.decode('utf-8'):
        click.echo("Your ssh-keys are configured correctly for access to github!")
        return True
    else:
        return False


def ssh_add():
    child = pexpect.spawn('ssh-add')
    child.interact()


def get_valid_keys():
    ls_proc = sp_run(['ls', '-al', str(Path.home() / '.ssh'), '|', 'grep', 'id'])
    return [key for key in SUPPORTED_KEYS
            if key in ls_proc.stdout.decode()]


def create_key():
    email = click.prompt('Enter your github email address:')
    child = pexpect.spawn(
        f'ssh-keygen -t ed25519 -C {email}'
    )
    child.interact()


def start_agent():
    # Check if agent is operational
    # if not running, start with
    ssh_agent_helper_path = Path(__file__).parent / 'ssh-agent-helper'
    child = pexpect.spawn(f'source {ssh_agent_helper_path}')
    child.interact()


def process_prompt_value(value, prompt_type, choices):
    if value is not None:
        index = prompt_type(value)
        return choices.choices[index]


def prompt_from_options(prompt_text: str, options: List[str]):
    choices = click.Choice(options)
    prompt_type = click.IntRange(min=0, max=len(options)-1)
    prompt_text = '{}:\n{}\n'.format(
        prompt_text,
        '\n'.join(f'{idx: >4}: {c}' for idx, c in enumerate(options))
    )
    value = click.prompt(
        prompt_text,
        type=choices,
        show_choices=False,
        value_proc=lambda x: process_prompt_value(x, prompt_type, choices),
    )
    return value


def add_key_to_gh(pub_key: str):
    key_path = Path.home() / '.ssh' / pub_key
    click.echo('Attempting to log into github cli.  This may open a browser...')
    # authenticate gh cli
    auth_child = pexpect.spawn('gh auth login')
    auth_child.interact()
    click.echo('checking authentication...')
    # add key
    click.echo('Authenticated!  Adding key to account')
    add_child = pexpect.spawn(f'gh ssh-key add {key_path} --type signing')
    add_child.interact()


def key_guide():
    click.echo('Starting github ssh key setup...')

    if ssh_is_enabled():
        return

    # Start the actual setup process
    # https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

    # Check for existing ssh keys
    click.echo('Checking for existing keys...')
    valid_keys = get_valid_keys()
    if valid_keys:
        click.echo(f"compatible key(s) found: {valid_keys}")
    else:
        click.echo("no compatible keys found, setting up new key")
        create_key()
        # if none exist, generate a new one

    # Start ssh-agent and authenticate keys
    click.echo("Starting ssh agent")
    start_agent()

    # Add SSH key to your github account
    click.echo("Add the ssh-key to your github account")
    options = get_valid_keys()
    key = prompt_from_options("Select the key used for github (by number)", options)
    click.echo(f"Chosen key: {key}, copied to clipboard")


if __name__ == "__main__":
    key_guide()
