from click import echo


def rg_id_uniqueness(ctx, metadata):
    logger = ctx.obj['LOGGER']
    logger.info("Start checking read group ID uniqueness in %s" % ctx.obj['subdir'])

    checks = ctx.obj['submission_report']['validation']['checks']
    checks.append({
        'check': __name__.split('.')[-1],
        'message': None,
        'status': None
    })

    if not metadata.get('read_groups'):
        message = "No read group information defined in the metadata JSON"
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
        return

    rg_ids = set()
    duplicated_ids = []
    for rg in metadata.get('read_groups'):
        if 'submitter_read_group_id' not in rg:
            message = "Required field 'submitter_read_group_id' not found in metadata JSON"
            logger.error(message)
            checks[-1]['message'] = message
            checks[-1]['status'] = 'INVALID'
            return

        if rg['submitter_read_group_id'] in rg_ids:
            duplicated_ids.append(rg['submitter_read_group_id'])
        else:
            rg_ids.add(rg['submitter_read_group_id'])

    if duplicated_ids:
        message =  "'submitter_read_group_id' duplicated in metadata: '%s'" % \
            ', '.join(duplicated_ids)
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
    else:
        checks[-1]['status'] = 'VALID'
        message = "Read group ID uniqueness check status: VALID"
        checks[-1]['message'] = message
        logger.info(message)
