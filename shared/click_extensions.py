import warnings

import click
from click.exceptions import UsageError
from click._compat import get_text_stderr
from click.utils import echo


def _show_usage_error(self, file=None):
    if file is None:
        file = get_text_stderr()
    color = None
    echo('Error: %s' % self.format_message(), file=file, color=color)
    if self.ctx is not None:
        echo('', file=file)
        color = self.ctx.color
        echo(self.ctx.get_help() + '\n', file=file, color=color)


UsageError.show = _show_usage_error


class ClickMutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.exclusive_with:list = kwargs.pop("exclusive_with")

        assert self.exclusive_with, "'exclusive_with' parameter required"
        super(ClickMutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt:bool = self.name in opts
        for mutex_opt in self.exclusive_with:
            if mutex_opt in opts:
                if current_opt:
                    raise UsageError("'" + str(self.name) + "' is mutually exclusive with " + str(mutex_opt) + ".",
                                     ctx=ctx)
                else:
                    self.prompt = None
        return super(ClickMutex, self).handle_parse_result(ctx, opts, args)


class ClickRequiredIfPresent(click.Option):
    def __init__(self, *args, **kwargs):
        self.required_if:list = kwargs.pop("required_if")

        assert self.required_if, "'required_if' parameter required"
        super(ClickRequiredIfPresent, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt:bool = self.name in opts
        for req_opt in self.required_if:
            if req_opt in opts:
                if not current_opt:
                    raise UsageError("'" + str(self.name) + "' is required if '" + str(req_opt) + "' is specified.",
                                     ctx=ctx)
                else:
                    self.prompt = None
        return super(ClickRequiredIfPresent, self).handle_parse_result(ctx, opts, args)


class ClickCommaSeparatedList(click.ParamType):
    name = "CSV"

    def convert(self, value, param, ctx):
        return value.split(',')


class ClickKeyValue(click.ParamType):
    name = "Key=Value"

    def convert(self, value, param, ctx):
        parts = value.split('=', 1)
        if len(parts) < 2:
            raise UsageError(f"Invalid argument: {value}: must be in Key=Value form.", ctx=ctx)
        return parts[0], parts[1]


class ClickKeyValueCSV(click.ParamType):
    name = "Key=Value[,...]"

    def convert(self, value, param, ctx):
        values = value.split(',')
        pairs = []
        for v in values:
            parts = v.split('=', 1)
            if len(parts) < 2:
                raise UsageError(f"Invalid argument: {v}: must be in Key=Value form.", ctx=ctx)
            pairs.append((parts[0], parts[1]))
        return pairs


class ClickRequires(click.ParamType):
    pass


CSV = ClickCommaSeparatedList()
KeyValue = ClickKeyValue()
KeyValueCSV = ClickKeyValueCSV()


class DefaultGroup(click.Group):
    """Invokes a subcommand marked with `default=True` if any subcommand not
    chosen.
    :param default_if_no_args: resolves to the default command if no arguments
                               passed.
    """

    def __init__(self, *args, **kwargs):
        # To resolve as the default command.
        if not kwargs.get('ignore_unknown_options', True):
            raise ValueError('Default group accepts unknown options')
        self.ignore_unknown_options = True
        self.default_cmd_name = kwargs.pop('default', None)
        self.default_if_no_args = kwargs.pop('default_if_no_args', False)
        super(DefaultGroup, self).__init__(*args, **kwargs)

    def set_default_command(self, command):
        """Sets a command function as the default command."""
        cmd_name = command.name
        self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx, args):
        if not args and self.default_if_no_args:
            args.insert(0, self.default_cmd_name)
        return super(DefaultGroup, self).parse_args(ctx, args)

    def get_command(self, ctx, cmd_name):
        if cmd_name not in self.commands:
            # No command name matched.
            ctx.arg0 = cmd_name
            cmd_name = self.default_cmd_name
        return super(DefaultGroup, self).get_command(ctx, cmd_name)

    def resolve_command(self, ctx, args):
        base = super(DefaultGroup, self)
        cmd_name, cmd, args = base.resolve_command(ctx, args)
        if hasattr(ctx, 'arg0'):
            args.insert(0, ctx.arg0)
            cmd_name = cmd.name
        return cmd_name, cmd, args

    def format_commands(self, ctx, formatter):
        formatter = DefaultCommandFormatter(self, formatter, mark='*')
        return super(DefaultGroup, self).format_commands(ctx, formatter)

    def command(self, *args, **kwargs):
        default = kwargs.pop('default', False)
        decorator = super(DefaultGroup, self).command(*args, **kwargs)
        if not default:
            return decorator
        warnings.warn('Use default param of DefaultGroup or '
                      'set_default_command() instead', DeprecationWarning)

        def _decorator(f):
            cmd = decorator(f)
            self.set_default_command(cmd)
            return cmd

        return _decorator


class DefaultCommandFormatter(object):
    """Wraps a formatter to mark a default command."""

    def __init__(self, group, formatter, mark='*'):
        self.group = group
        self.formatter = formatter
        self.mark = mark

    def __getattr__(self, attr):
        return getattr(self.formatter, attr)

    def write_dl(self, rows, *args, **kwargs):
        rows_ = []
        for cmd_name, help in rows:
            if cmd_name == self.group.default_cmd_name:
                rows_.insert(0, (cmd_name + self.mark, help))
            else:
                rows_.append((cmd_name, help))
        return self.formatter.write_dl(rows_, *args, **kwargs)