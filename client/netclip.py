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
