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

    netclip.copy(working_dir=working_dir,
                 no_copy=no_copy,
                 no_print=no_print,
                 clip_name=clip_name)


if __name__ == '__main__':
    copy()
