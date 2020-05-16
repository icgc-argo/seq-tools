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

    if not metadata.get('samples'):
        message = "Missing 'samples' section in the metadata JSON"
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
        logger.error(message)
        return

    if len(metadata.get('samples')) != 1:
        message =  "'samples' section must contain exactly one sample in metadata, %s found" % \
            len(metadata.get('samples'))
        checks[-1]['message'] = message
        checks[-1]['status'] = 'INVALID'
        logger.error(message)
    else:
        message = "One and only one sample check status: VALID"
        checks[-1]['status'] = 'VALID'
        checks[-1]['message'] = message
        logger.info(message)
