# -*- coding: utf-8 -*-

"""
    Copyright (c) 2020, Ontario Institute for Cancer Research (OICR).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Authors:
        Junjun Zhang <junjun.zhang@oicr.on.ca>
"""


import click
import json
import time
from seq_tools import __version__ as ver
from ..validation import perform_validation
from ..utils import ntcnow_iso, check_for_update


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('seq-tools %s' % ver)
    ctx.exit()


@click.group()
@click.option('--debug/--no-debug', '-d', is_flag=True, default=False,
              help='Show debug information in STDERR.')
@click.option('--ignore-update', '-i', is_flag=True, default=False,
              help='Keep using the current version of seq-tools, ignore available update.')
@click.option('--check-prerelease', '-p', is_flag=True, default=False,
              help='In addition to stable release, also check new pre-release update if selected.')
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show seq-tools version.')
@click.pass_context
def main(ctx, debug, ignore_update, check_prerelease):
    # initializing ctx.obj
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug

    check_for_update(ctx, ignore_update, check_prerelease)


@main.command()
@click.option('--metadata', '-m', help='submission metadata as a JSON string')
@click.argument('submission_dir', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def validate(ctx, submission_dir, metadata):
    """
    Perform validation on submission directory or metadata.
    """
    if not (submission_dir or metadata):
        click.echo(
            'Must specify one or more submission directories or metadata as a JSON string.'
        )
        ctx.abort()
    elif submission_dir and metadata:
        click.echo('Can not specify both submission dir and metadata')
        ctx.abort()

    if submission_dir:
        summary_report = {
            "summary": {},
            "version": ver,
            "status": [],
            "started_at": ntcnow_iso(),
            "ended_at": None,
            "message": "Please check 'report.json' in individual submission "
            "dir for more details."
        }

        total = len(submission_dir)
        current = 0
        for subdir in submission_dir:
            current += 1

            perform_validation(ctx, subdir=subdir)
            status = ctx.obj['submission_report']['validation']['status']
            click.echo('submission_dir: %s, status: %s, current_time: %s, progress: %s/%s' % (
                subdir, status, ntcnow_iso(), current, total
            ), err=True)

            summary_report['status'].append({
                'submission_dir': subdir,
                'status': status
            })

            if status not in summary_report['summary']:
                summary_report['summary'][status] = 0
            summary_report['summary'][status] += 1

        click.echo('', err=True)
        summary_report['ended_at'] = ntcnow_iso()

        # wait a bit to avoid mixing STDOUT with STDERR in terminal display
        time.sleep(.3)
        click.echo(json.dumps(summary_report))
    else:
        perform_validation(ctx, metadata=metadata)
