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
from ..utils import find_files, ntcnow_iso


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


def perform_validation(ctx, metadata_file=None, data_dir=None, metadata_str=None):
    if not (metadata_file or metadata_str):
        echo('Must specify one or more submission metadata files or metadata as a JSON string.', err=True)
        ctx.abort()
    elif metadata_file and metadata_str:
        echo('Can not specify both metadata file and metadata string', err=True)
        ctx.abort()

    if metadata_file:
        metadata_file = os.path.realpath(metadata_file)

    if data_dir:
        data_dir = os.path.realpath(data_dir)

    if not data_dir and metadata_file:
        data_dir = os.path.dirname(os.path.realpath(metadata_file))

    # ctx.obj['data_dir'] = data_dir
    logger = ctx.obj['LOGGER']

    # initialize validate status
    ctx.obj['validation_report'] = {
        'tool': {
            'name': 'seq-tools',
            'version': ver
        },
        'metadata_file': os.path.realpath(metadata_file) if metadata_file else None,
        'data_dir': data_dir if data_dir else None,
        'data_files': find_files(
            data_dir, r'^.+?\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'
        ) if data_dir else [],
        'started_at': ntcnow_iso(),
        'ended_at': None,
        'validation': {
            'status': None,
            'message': 'Please see individual checks for details',
            'checks': []
        }
    }

    # get SONG metadata
    if metadata_file:
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                ctx.obj['validation_report']['metadata_file'] = metadata_file

            if not isinstance(metadata, dict):
                message = "Metadata file '%s' is not a JSON object. " \
                    "Unable to continue with further checks." % metadata_file
                logger.info(message)
                ctx.obj['validation_report']['validation']['message'] = message
                ctx.obj['validation_report']['validation']['status'] = "INVALID"
        except Exception as ex:
            message = "Failed to open '%s'. " \
                "Unable to continue with further checks. Please make sure it is a valid JSON file " \
                "and readable. Error message: %s" % (metadata_file, str(ex))
            logger.info(message)
            ctx.obj['validation_report']['validation']['message'] = message
            ctx.obj['validation_report']['validation']['status'] = "INVALID"

    else:  # metadata string supplied
        ctx.obj['validation_report'].pop('data_files')  # files not applicable here
        try:
            metadata = json.loads(metadata_str)

            if not isinstance(metadata, dict):
                message = "Provided metadata is not a JSON object. " \
                    "Unable to continue with further checks." % metadata_file
                logger.info(message)
                ctx.obj['validation_report']['validation']['message'] = message
                ctx.obj['validation_report']['validation']['status'] = "INVALID"
        except Exception as ex:
            message = "Unable to load metadata, please ensure it's a valid JSON " \
                "string. Error: %s" % str(ex)
            logger.info(message)
            ctx.obj['validation_report']['validation']['message'] = message
            ctx.obj['validation_report']['validation']['status'] = "INVALID"

        ctx.obj['validation_report']['metadata'] = '<supplied as a JSON string>'

    if ctx.obj['validation_report']['validation']['status'] != "INVALID":
        for c in checkers:  # perform validation checks one by one
            checker_code = c.split('_')[0]
            # skip these checkers that involve sequencing file
            # when no submission dir specified
            if not data_dir and checker_code[0:2] in ('c6', 'c7', 'c8', 'c9'):
                continue
            checker = checkers[c].Checker(ctx, metadata)
            checker.check()

        # aggregate status from validation checks
        check_status = set()
        for c in ctx.obj['validation_report']['validation']['checks']:
            check_status.add(c['status'])

        if 'INVALID' in check_status:
            ctx.obj['validation_report']['validation']['status'] = 'INVALID'
        elif 'UNKNOWN' in check_status:
            ctx.obj['validation_report']['validation']['status'] = 'UNKNOWN'
        elif 'WARNING' in check_status:
            ctx.obj['validation_report']['validation']['status'] = 'WARNING'
        elif 'PASS' in check_status and len(check_status) == 1:  # only has 'PASS' status
            ctx.obj['validation_report']['validation']['status'] = 'PASS'
        else:  # should never happen
            ctx.obj['validation_report']['validation']['status'] = None

    # record completing time
    ctx.obj['validation_report']['ended_at'] = ntcnow_iso()

    if metadata_file:
        message = "Validation completed for '%s', status: %s. " \
            "Please find details in report JSONL file(s)." % \
            (metadata_file, ctx.obj['validation_report']['validation']['status'])
        logger.info(message)
    else:
        message = "Validation completed for the input metadata, status: %s. " \
            "Please find detailed report in STDOUT." % \
            ctx.obj['validation_report']['validation']['status']
        logger.info(message)
        echo(json.dumps(ctx.obj['validation_report']))
