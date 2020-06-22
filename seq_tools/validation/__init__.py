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
        echo('Must specify submission directory or metadata as JSON string.', err=True)
        ctx.abort()
    elif subdir and metadata:
        echo('Can not specify both submission dir and metadata', err=True)
        ctx.abort()

    metadata_file = 'sequencing_experiment.json'

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
                    subdir, metadata_file), 'r') as f:
                metadata = json.load(f)
                ctx.obj['submission_report']['metadata'] = metadata_file

            if not isinstance(metadata, dict):
                message = "Metadata file '%s' is not a JSON object. " \
                    "Unable to continue with further checks." % metadata_file
                logger.info(message)
                ctx.obj['submission_report']['validation']['message'] = message
                ctx.obj['submission_report']['validation']['status'] = "INVALID"
        except FileNotFoundError:
            message = "Metadata file '%s' not found under '%s'. " \
                 "Unable to continue with further checks." % (metadata_file, os.path.join(subdir, ''))
            logger.info(message)
            ctx.obj['submission_report']['validation']['message'] = message
            ctx.obj['submission_report']['validation']['status'] = "INVALID"
        except Exception as ex:
            message = "Failed to open '%s' under '%s'. " \
                "Unable to continue with further checks. Error message: %s" % \
                (metadata_file, os.path.join(subdir, ''), str(ex))
            logger.info(message)
            ctx.obj['submission_report']['validation']['message'] = message
            ctx.obj['submission_report']['validation']['status'] = "INVALID"

    else:  # metadata supplied
        ctx.obj['submission_report'].pop('files')  # files not applicable here
        try:
            metadata = json.loads(metadata)

            if not isinstance(metadata, dict):
                message = "Provided metadata is not a JSON object. " \
                    "Unable to continue with further checks." % metadata_file
                logger.info(message)
                ctx.obj['submission_report']['validation']['message'] = message
                ctx.obj['submission_report']['validation']['status'] = "INVALID"
        except Exception as ex:
            message = "Unable to load metadata, please ensure it's a valid JSON " \
                "string. Error: %s" % str(ex)
            logger.info(message)
            ctx.obj['submission_report']['validation']['message'] = message
            ctx.obj['submission_report']['validation']['status'] = "INVALID"

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
        elif 'UNKNOWN' in check_status:
            ctx.obj['submission_report']['validation']['status'] = 'UNKNOWN'
        elif 'WARNING' in check_status:
            ctx.obj['submission_report']['validation']['status'] = 'WARNING'
        elif 'PASS' in check_status and len(check_status) == 1:  # only has 'PASS' status
            ctx.obj['submission_report']['validation']['status'] = 'PASS'
        else:  # should never happen
            ctx.obj['submission_report']['validation']['status'] = None

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
