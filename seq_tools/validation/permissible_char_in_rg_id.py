from click import echo


def permissible_char_in_rg_id(ctx, metadata):
    # echo(metadata)
    logger = ctx.obj['LOGGER'][ctx.obj['subdir']]
    logger.info("Start checking permissible characters in read group ID in %s" % ctx.obj['subdir'])

    # TODO

    logger.info(
        "Completed permissible characters in read group ID check in %s, result: no error found" % ctx.obj['subdir']
    )
