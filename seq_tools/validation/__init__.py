import os
import json
from click import echo
from ..utils import initialize_log
from .rg_id_uniqueness import rg_id_uniqueness
from .permissible_char_in_rg_id import permissible_char_in_rg_id


def perform_validation(ctx, subdir):
    # initialize logger
    ctx.obj['subdir'] = subdir
    initialize_log(ctx, subdir)
    logger = ctx.obj['LOGGER']

    # initialize validate status
    ctx.obj['submission_report'] = {
        'submission_directory': os.path.realpath(subdir),
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
    except:
        message = "Unable to open sequencing_experiment.json in: '%s'" % subdir
        logger.error(message)
        ctx.obj['submission_report']['validation']['message'] = message
        ctx.obj['submission_report']['validation']['status'] = "INVALID"
        logger.info("Validation completed for '%s', result: %s" % \
            (subdir, ctx.obj['submission_report']['validation']['status'])
        )
        return  # unable to continue with the validation

    # check read group ID uniqueness
    rg_id_uniqueness(ctx, metadata)

    # check permissible characters in read group ID
    permissible_char_in_rg_id(ctx, metadata)

    # TODO: add more checks here

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
        os.symlink(os.path.realpath(report_filename), os.path.join(subdir, 'report.json'))

    message = "Validation completed for '%s', status: %s. Please find details in 'report.json'." % \
        (os.path.realpath(subdir), ctx.obj['submission_report']['validation']['status'])
    logger.info(message)
    echo(message)
