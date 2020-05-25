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
import sys
import json
from click import echo
from seq_tools import __version__ as ver
from ..utils import initialize_log, find_files, ntcnow_iso


path = list(sys.path)
sys.path.insert(0, os.path.dirname(__file__))
moduleFiles = sorted(find_files(os.path.dirname(__file__), r'^c[0-9]+_.*?\.py$'))
checkers = {}
try:
    # load checker modules
    for m in moduleFiles:
        moduleName = os.path.splitext(m)[0]
        checkers[moduleName] = __import__(moduleName)
finally:
    sys.path[:] = path


def perform_validation(ctx, subdir=None, metadata=None):
    if not (subdir or metadata):
        echo(
            'Must specify submission directory or metadata as JSON string.'
        )
        ctx.abort()
    elif subdir and metadata:
        echo('Can not specify both submission dir and metadata')
        ctx.abort()

    # initialize logger
    ctx.obj['subdir'] = subdir
    initialize_log(ctx, subdir)
    logger = ctx.obj['LOGGER']

    # initialize validate status
    ctx.obj['submission_report'] = {
        'tool': {
            'name': 'seq-tools',
            'version': ver
        },
        'submission_directory': os.path.realpath(subdir) if subdir else None,
        'metadata': None,
        'files': find_files(
            subdir, r'^.+?\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'
        ) if subdir else [],
        'started_at': ntcnow_iso(),
        'ended_at': None,
        'validation': {
            'status': None,
            'message': 'Please see individual checks for details',
            'checks': []
        }
    }

    # get SONG metadata
    if subdir:
        try:
            with open(os.path.join(
                    subdir, "sequencing_experiment.json"), 'r') as f:
                metadata = json.load(f)
                ctx.obj['submission_report']['metadata'] = \
                    "sequencing_experiment.json"
        except Exception:
            message = "Failed to open sequencing_experiment.json in: '%s'. " \
                "Unable to continue with further checks." % subdir
            logger.info(message)
            ctx.obj['submission_report']['validation']['message'] = message
            ctx.obj['submission_report']['validation']['status'] = "INVALID"

    else:  # metadata supplied
        ctx.obj['submission_report'].pop('files')  # files not applicable here
        try:
            metadata = json.loads(metadata)
        except Exception as ex:
            logger.info(
                "Unable to load metadata, please ensure it's valid JSON "
                "string. Error: %s" % str(ex))
            ctx.abort()

        ctx.obj['submission_report']['metadata'] = '<supplied as JSON string>'

    if ctx.obj['submission_report']['validation']['status'] != "INVALID":
        for c in checkers:  # perform validation checks one by one
            checker_code = c.split('_')[0]
            # skip these checkers that involve sequencing file
            # when no submission dir specified
            if not subdir and checker_code[0:2] in ('c6', 'c7', 'c8', 'c9'):
                continue
            checker = checkers[c].Checker(ctx, metadata)
            checker.check()

        # aggregate status from validation checks
        check_status = set()
        for c in ctx.obj['submission_report']['validation']['checks']:
            check_status.add(c['status'])

        if 'INVALID' in check_status:
            ctx.obj['submission_report']['validation']['status'] = 'INVALID'
        elif 'WARNING' in check_status:
            ctx.obj['submission_report']['validation']['status'] = 'WARNING'
        elif 'VALID' in check_status:
            ctx.obj['submission_report']['validation']['status'] = 'VALID'
        else:  # should never happen
            ctx.obj['submission_report']['validation']['status'] = 'UNKNOWN'

    # complete the validation
    ctx.obj['submission_report']['ended_at'] = ntcnow_iso()
    if subdir:
        log_filename = os.path.splitext(
            os.path.basename(logger.handlers[0].baseFilename))[0]
        report_filename = os.path.join(
            subdir, 'logs', '%s.report.json' % log_filename)
        with open(report_filename, 'w') as f:
            f.write(json.dumps(ctx.obj['submission_report'], indent=2))
            try:
                os.remove(os.path.join(subdir, 'report.json'))
            except OSError:
                pass
            os.symlink(
                os.path.join('logs', '%s.report.json' % log_filename),
                os.path.join(subdir, 'report.json'))

        message = "Validation completed for '%s', status: %s. " \
            "Please find details in 'report.json' in the submission directory." % \
            (os.path.realpath(subdir),
                ctx.obj['submission_report']['validation']['status'])
        logger.info(message)
    else:
        message = "Validation completed for the input metadata, status: %s. " \
            "Please find detailed report in STDOUT." % \
            ctx.obj['submission_report']['validation']['status']
        logger.info(message)
        echo(json.dumps(ctx.obj['submission_report']))
