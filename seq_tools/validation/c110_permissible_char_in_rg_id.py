import re
from click import echo


def check(ctx, metadata):
    logger = ctx.obj['LOGGER']
    logger.info("Start checking read group ID uniqueness in %s" % ctx.obj['subdir'])

    checks = ctx.obj['submission_report']['validation']['checks']
    checks.append({
        'check': __name__.split('.')[-1],
        'status': None,
        'message': None
    })

    if not metadata.get('read_groups'):
        message = "No read group information defined in the metadata JSON"
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
        return

    offending_ids = set()
    for rg in metadata.get('read_groups'):
        if 'submitter_read_group_id' not in rg:
            message = "Required field 'submitter_read_group_id' not found in metadata JSON"
            logger.error(message)
            checks[-1]['message'] = message
            checks[-1]['status'] = 'INVALID'
            return

        if not re.match(r'^[a-zA-Z0-9_\.\-]{2,}$', rg['submitter_read_group_id']):
            offending_ids.add(rg['submitter_read_group_id'])

    if offending_ids:
        message =  "'submitter_read_group_id' in metadata contains invalid character or " \
            "is shorter then 2 characters: '%s'. " \
            "Permissible characters include: a-z, A-Z, 0-9, - (hyphen), " \
            "_ (underscore) and . (dot)" % ', '.join(offending_ids)
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
    else:
        checks[-1]['status'] = 'VALID'
        message = "Read group ID permissible character check status: VALID"
        checks[-1]['message'] = message
        logger.info(message)
