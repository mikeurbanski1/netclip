import click
import os
from pathlib import Path
import pyperclip
import sys

from shared.click_extensions import *


DEFAULT_CLIP_NAME = '.default'


@click.group(cls=DefaultGroup, default='clip', default_if_no_args=True)
@click.pass_context
def execute(ctx):
    """Netclip is (or, will be) a utility for working with multiple saved copy/paste items, or "clips", over a network
    to be used with multiple devices and/or users. Its intent is to be command-line friendly first.

    Currently, it functions as a local clipboard utility, saving named clips and accessing them. It can be considered
    a convenience wrapper of more verbose clipboard tools like xclip.

    This program, netclip, is the entrypoint for all client-operations, namely clipping, copying, and working with
    saved clips. It contains subcommands for each of these operations. The default subcommand, if none is specified,
    is "clip". For convenience, additional python files exist to bypass the more verbose subcommand syntax.

    Use 'netclip COMMAND --help' to see descriptions of each subcommand.

    Clips are stored in a local working directory defaulting to ~/.netclip. All commands can take the name of a clip as
    the argument. A default clip, '.default', will be used whenever the clip name is omitted. The default clip is meant
    to be used for temporary items that do not need to be saved.
    """
    pass


@execute.command()
@click.option('-c', '--use-clipboard', is_flag=True, envvar='NETCLIP_USE_CLIPBOARD',
              help='Do not read input from stdin; instead, use the existing clipboard contents as the input.')
@click.option('-n', '--no-copy', is_flag=True, envvar='NETCLIP_NO_COPY',
              help='Do not copy the input text to the clipboard; just save it to the clip.')
@click.option('--no-overwrite', is_flag=True, envvar='NETCLIP_NO_OVERWRITE',
              help='Do not overwrite any existing clips (fail instead), except for the default clip.')
@click.option('-d', '--working-dir', type=click.Path(exists=False), envvar='NETCLIP_WORKING_DIR',
              help='The directory in which to store clips. Will be created if it does not exist. Defaults to '
                   '~/.netclip')
@click.argument('clip_name', envvar='NETCLIP_CLIP', default=DEFAULT_CLIP_NAME)
def clip(use_clipboard: bool,
         no_copy: bool,
         no_overwrite: bool,
         working_dir: str,
         clip_name: str):
    """Creates or updates a saved clip from the specified input source (stdin, or the current clipboard contents)."""

    if not working_dir:
        working_dir = os.path.join(str(Path.home()), '.netclip')

    # print('Use clipboard: ' + str(use_clipboard))
    # print('No copy: ' + str(no_copy))
    # print('No overwrite: ' + str(no_overwrite))
    # print('Working dir: ' + str(working_dir))
    # print('Clip name: ' + str(clip_name))

    Path(working_dir).mkdir(parents=True, exist_ok=True)

    clip_path = os.path.join(working_dir, clip_name)
    exists = Path(clip_path).exists()

    if exists and no_overwrite and clip_name != DEFAULT_CLIP_NAME:
        print(f"Error: clip '{clip_name}' already exists in {working_dir}, and --no-overwrite was set.")
        exit(1)

    text = pyperclip.paste() if use_clipboard else sys.stdin.read()

    if not no_copy:
        pyperclip.copy(text)

    with open(clip_path, 'w') as writer:
        writer.write(text)

    print(f'Saved to {clip_path}')


@execute.command()
@click.option('-d', '--working-dir', type=click.Path(exists=False), envvar='NETCLIP_WORKING_DIR',
              help='The directory in which to read clips. Will be created if it does not exist. Defaults to '
                   '~/.netclip')
@click.option('-n', '--no-copy', is_flag=True, envvar='NETCLIP_NO_COPY',
              help='Do not copy the saved clip text to the clipboard; just print it (unless --no-print was set).')
@click.option('-p', '--no-print', is_flag=True, envvar='NETCLIP_NO_PRINT',
              help='Do not print the saved clip text; just copy it (unless --no-copy was set).')
@click.argument('clip_name', envvar='NETCLIP_CLIP', default=DEFAULT_CLIP_NAME)
def copy(working_dir: str,
         no_copy: bool,
         no_print: bool,
         clip_name: str):
    """Reads a saved clip and writes it to the specified output sources (stdout and/or the clipboard).

    Currently, a limitation exists that prevents both writing output and saving to the clipboard when the output is
    piped to another command. It will cause the program to hang indefinitely. This is because setting the clipboard
    itself uses piping to a subprocess, and these operations conflict.

    When piping the output to another command, use the --no-copy option to suppress updating the clipboard.
    """

    if not working_dir:
        working_dir = os.path.join(str(Path.home()), '.netclip')

    # print('Working dir: ' + str(working_dir))
    # print('Clip name: ' + str(clip_name))

    Path(working_dir).mkdir(parents=True, exist_ok=True)

    clip_path = os.path.join(working_dir, clip_name)
    exists = Path(clip_path).exists()

    if not exists:
        print(f"Error: clip '{clip_name}' does not exist in {working_dir}.")
        exit(1)

    with open(clip_path, 'r') as reader:
        text = reader.read()

    if not no_print:
        print(text, end='')

    # TODO this breaks if the command is piped to something else.
    if not no_copy:
        pyperclip.copy(text)


if __name__ == '__main__':
    execute()
