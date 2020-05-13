import os
import json
from click import echo
from ..utils import initialize_log
from .rg_id_uniq import rg_id_uniq
from .permissible_char_in_rg_id import permissible_char_in_rg_id


def perform_validation(ctx, subdirs):
    for subdir in subdirs:
        # initialize logger
        ctx.obj['subdir'] = subdir
        initialize_log(ctx, subdir)

        # get SONG metadata
        try:
            with open(os.path.join(subdir, "sequencing_experiment.json"), 'r') as f:
                metadata = json.load(f)
        except:
            ctx.obj['LOGGER'].critical("Unable to open sequencing_experiment.json in: '%s'" % subdir)
            ctx.abort()

        # check read group ID uniqueness
        rg_id_uniq(ctx, metadata)

        # check permissible characters in read group ID
        permissible_char_in_rg_id(ctx, metadata)
