import os
import json
from click import echo
from ..utils import initialize_log
from .rg_id_uniq import rg_id_uniq
from .permissible_char_in_rg_id import permissible_char_in_rg_id


def perform_validation(ctx, subdirs):
    checked = set()
    for subdir in subdirs:
        if subdir in checked:  # avoid checking the same submission dir more than once
            continue
        checked.add(subdir)

        # initialize logger
        ctx.obj['subdir'] = subdir
        initialize_log(ctx, subdir)
        logger = ctx.obj['LOGGER'][subdir]

        # initialize validate status
        ctx.obj['submission_report'] = {
            'submission_directory': os.path.realpath(subdir),
            'validation': {
                    'status': None
            }
        }

        # get SONG metadata
        try:
            with open(os.path.join(subdir, "sequencing_experiment.json"), 'r') as f:
                metadata = json.load(f)
        except:
            logger.error("Unable to open sequencing_experiment.json in: '%s'" % subdir)
            ctx.obj['submission_report']['validation']['status'] = "Invalid"
            logger.info("Validation completed for '%s', result: %s" % \
                (subdir, ctx.obj['submission_report']['validation']['status'])
            )
            continue  # unable to continue with the validation

        # check read group ID uniqueness
        rg_id_uniq(ctx, metadata)

        # check permissible characters in read group ID
        permissible_char_in_rg_id(ctx, metadata)

        # complete the validation
        logger.info("Validation completed for '%s', result: %s" % \
            (subdir, ctx.obj['submission_report']['validation']['status'])
        )
