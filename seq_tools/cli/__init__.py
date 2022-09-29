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

import os
import click
import json
import time
from seq_tools import __version__ as ver
from ..validation import perform_validation
from ..utils import ntcnow_iso, check_for_update, initialize_log


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
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show seq-tools version.')
@click.pass_context
def main(ctx, debug, ignore_update):
    # initializing ctx.obj
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug

    check_for_update(ctx, ignore_update)


@main.command()
@click.option('--metadata_str', '-s', help='submission metadata as a JSON string')
@click.option('--data_dir', '-d', type=click.Path(exists=True),
              help='path containing submission data files')
@click.option('--skip_md5sum_check', is_flag=True, help='skip md5sum check, save time for large files')
@click.option('--skip_strandedness_check', is_flag=True, help='skip strandedness check, save time for large files')
@click.argument('metadata_file', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def validate(ctx, metadata_str, metadata_file, data_dir, skip_md5sum_check,skip_strandedness_check):
    """
    Perform validation on metadata file(s) or metadata string.
    """
    if not (metadata_file or metadata_str):
        click.echo(
            'Must specify one or more submission metadata files or metadata as a JSON string.\n'
        )
        click.echo(ctx.get_help())
        ctx.exit()
    elif metadata_file and metadata_str:
        click.echo('Can not specify both metadata file and metadata string.\n')
        click.echo(ctx.get_help())
        ctx.exit()

    initialize_log(ctx, os.getcwd())
    logger = ctx.obj['LOGGER']
    log_file = logger.handlers[0].baseFilename

    if metadata_file:
        summary_report = {
            "summary": {},
            "version": ver,
            "started_at": ntcnow_iso(),
            "ended_at": None,
            "log_file": log_file,
            "message": "Please check out details in validation report",
            "reports": []
        }

        total = len(metadata_file)
        current = 0
        validation_reports = {}
        click.echo('Start validating %s metadata file(s), current_time: %s. ' % (total, ntcnow_iso()) +
                   'Please be patient, it may take sometime.')
        for metafile in metadata_file:
            current += 1

            perform_validation(ctx, metadata_file=metafile, data_dir=data_dir, skip_md5sum_check=skip_md5sum_check,skip_strandedness_check=skip_strandedness_check)

            status = ctx.obj['validation_report']['validation']['status']
            status_with_stype = status
            if status == 'INVALID':
                status_with_stype = click.style(status, fg="red")
            elif status == 'UNKNOWN':
                status_with_stype = click.style(status, fg="magenta")
            elif status == 'PASS-with-WARNING':
                status_with_stype = click.style(status, fg="yellow")
            elif status == 'PASS':
                status_with_stype = click.style(status, fg="green")

            click.echo('metadata_file: %s, status: %s, current_time: %s, progress: %s/%s' % (
                metafile, status_with_stype, ntcnow_iso(), current, total
            ), err=True)

            if status not in summary_report['summary']:
                summary_report['summary'][status] = 0
                validation_reports[status] = []

            summary_report['summary'][status] += 1
            validation_reports[status].append(ctx.obj['validation_report'])

        click.echo('', err=True)
        summary_report['ended_at'] = ntcnow_iso()

        # split report based on validation status
        for status in (
                    'INVALID',
                    'UNKNOWN',
                    'PASS-with-WARNING-and-SKIPPED-check',
                    'PASS-with-SKIPPED-check',
                    'PASS-with-WARNING',
                    'PASS'
                ):
            report_filename = 'validation_report.%s.jsonl' % status
            log_filename = os.path.splitext(os.path.basename(log_file))[0]
            report_file = os.path.join('logs', '%s.%s' % (log_filename, report_filename))
            with open(report_file, 'w') as f:
                if validation_reports.get(status):
                    for report in validation_reports[status]:
                        report.pop('data_files')  # could be a long list, remove for simplicity
                        # only keep checks whose status match the aggregated status for simpler report
                        selected_checks = []
                        for c in report['validation']['checks']:
                            if c['status'] in status:  # allow PASS and WARNING to be selected for PASS-with-WARNING
                                selected_checks.append(c)
                        report['validation']['checks'] = selected_checks

                        f.write("%s\n" % json.dumps(report))

            try:  # remove possible previous reports
                os.remove(report_filename)
            except OSError:  # ignore if file not exist
                pass

            if os.stat(report_file).st_size > 0:
                os.symlink(report_file, report_filename)
                summary_report['reports'].append(report_filename)

        # wait a bit to avoid mixing STDOUT with STDERR in terminal display
        time.sleep(.3)
        click.echo(json.dumps(summary_report))

    else:
        perform_validation(ctx, metadata_str=metadata_str)
