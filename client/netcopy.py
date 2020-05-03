import click

from client import netclip


@click.command()
@click.option('-d', '--working-dir', type=click.Path(exists=False), envvar='NETCLIP_WORKING_DIR',
              help='The directory in which to read clips. Will be created if it does not exist. Defaults to '
                   '~/.netclip')
@click.option('-n', '--no-copy', is_flag=True, envvar='NETCLIP_NO_COPY',
              help='Do not copy the saved clip text to the clipboard; just print it (unless --no-print was set).')
@click.option('-p', '--no-print', is_flag=True, envvar='NETCLIP_NO_PRINT',
              help='Do not print the saved clip text; just copy it (unless --no-copy was set).')
@click.argument('clip_name', envvar='NETCLIP_CLIP', default=netclip.DEFAULT_CLIP_NAME)
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

    netclip.copy(working_dir=working_dir,
                 no_copy=no_copy,
                 no_print=no_print,
                 clip_name=clip_name)


if __name__ == '__main__':
    copy()
