from click import echo


def rg_id_uniq(ctx, metadata):
    # echo(metadata)
    logger = ctx.obj['LOGGER'][ctx.obj['subdir']]
    logger.info("Start checking read group ID uniqueness in %s" % ctx.obj['subdir'])

    if not metadata.get('read_groups'):
        logger.info("No read group information defined in the metadata")
        ctx.obj['validation_error'] = True
        return

    rg_ids = set()
    for rg in metadata.get('read_groups'):
        if 'submitter_read_group_id' not in rg:
            logger.info("required field submitter_read_group_id not found in metadata")
            ctx.obj['validation_error'] = True
            return

        if rg['submitter_read_group_id'] in rg_ids:
            logger.warn(
                "submitter_read_group_id duplicated in metadata: %s" % rg['submitter_read_group_id']
            )
            ctx.obj['validation_error'] = True
            return
        else:
            rg_ids.add(rg['submitter_read_group_id'])

    logger.info(
        "Completed read group ID uniqueness check in %s, result: no error found" % ctx.obj['subdir']
    )
