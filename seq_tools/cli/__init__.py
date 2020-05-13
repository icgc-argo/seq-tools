import os
import logging
import click
import click_log
from seq_tools import __version__ as ver
from seq_tools import utils
from ..validation import perform_validation


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('seq-tools %s' % ver)
    ctx.exit()


@click.group()
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def main(ctx, debug):
    # initializing ctx.obj
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug


@main.command()
@click.argument('submission_dir', type=click.Path(exists=True), nargs=-1)
@click.pass_context
def validate(ctx, submission_dir):
    """
    Perform validation on submission folder(s).
    """
    if not submission_dir:
        click.echo('You must specify at least one submission directory.')
        ctx.abort()

    perform_validation(ctx, submission_dir)
