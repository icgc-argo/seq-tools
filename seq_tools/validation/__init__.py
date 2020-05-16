import os
import sys
import json
from click import echo
from ..utils import initialize_log, find_files


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


def perform_validation(ctx, subdir):
    # initialize logger
    ctx.obj['subdir'] = subdir
    initialize_log(ctx, subdir)
    logger = ctx.obj['LOGGER']

    # initialize validate status
    ctx.obj['submission_report'] = {
        'submission_directory': os.path.realpath(subdir),
        'metadata': None,
        'files': find_files(subdir, r'^.+?\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'),
        'validation': {
            'status': None,
            'message': 'Please see individual checks for details',
            'checks': []
        }
    }

    # get SONG metadata
    try:
        with open(os.path.join(subdir, "sequencing_experiment.json"), 'r') as f:
            metadata = json.load(f)
            ctx.obj['submission_report']['metadata'] = "sequencing_experiment.json"
    except:
        message = "Failed to open sequencing_experiment.json in: '%s'. " \
            "Unable to continue with further checks." % subdir
        logger.error(message)
        ctx.obj['submission_report']['validation']['message'] = message
        ctx.obj['submission_report']['validation']['status'] = "INVALID"

    if ctx.obj['submission_report']['validation']['status'] != "INVALID":
        for c in checkers:  # perform validation checks one by one
            checkers[c].check(ctx, metadata)

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
    log_filename = os.path.splitext(os.path.basename(logger.handlers[0].baseFilename))[0]
    report_filename = os.path.join(subdir, 'logs', '%s.report.json' % log_filename)
    with open(report_filename, 'w') as f:
        f.write(json.dumps(ctx.obj['submission_report'], indent=2))
        try:
            os.remove(os.path.join(subdir, 'report.json'))
        except OSError:
            pass
        os.symlink(os.path.join('logs', '%s.report.json' % log_filename), os.path.join(subdir, 'report.json'))

    message = "Validation completed for '%s', status: %s. Please find details in 'report.json'." % \
        (os.path.realpath(subdir), ctx.obj['submission_report']['validation']['status'])
    logger.info(message)
    echo(message)
