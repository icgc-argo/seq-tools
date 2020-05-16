from click import echo


def check(ctx, metadata):
    logger = ctx.obj['LOGGER']
    logger.info("Start checking platform unit uniqueness in %s" % ctx.obj['subdir'])

    checks = ctx.obj['submission_report']['validation']['checks']
    checks.append({
        'check': __name__.split('.')[-1],
        'status': None,
        'message': None
    })

    if not metadata.get('read_groups'):
        message = "Missing 'read_groups' section in the metadata JSON"
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
        return

    pus = set()
    duplicated_pus = []
    for rg in metadata.get('read_groups'):
        if 'platform_unit' not in rg:
            message = "Required field 'platform_unit' not found in metadata JSON"
            logger.error(message)
            checks[-1]['message'] = message
            checks[-1]['status'] = 'INVALID'
            return

        if rg['platform_unit'] in pus:
            duplicated_pus.append(rg['platform_unit'])
        else:
            pus.add(rg['platform_unit'])

    if duplicated_pus:
        message =  "'platform_unit' duplicated in metadata: '%s'" % \
            ', '.join(duplicated_pus)
        logger.error(message)
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
    else:
        checks[-1]['status'] = 'VALID'
        message = "Platform unit uniqueness check status: VALID"
        checks[-1]['message'] = message
        logger.info(message)
