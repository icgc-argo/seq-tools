import os
import re
from click import echo
import logging
import datetime


def initialize_log(ctx, dir):
    logger = logging.getLogger('seq_tools: %s' % dir)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s")

    logger.setLevel(logging.INFO)

    log_directory = os.path.join(dir, "logs")
    log_file = "%s.log" % re.sub(r'[-:.]', '_', datetime.datetime.utcnow().isoformat())
    ctx.obj['log_file'] = log_file
    log_file = os.path.join(log_directory, log_file)

    if not os.path.isdir(log_directory):
        os.mkdir(log_directory)

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)  # always set fh to debug
    fh.setFormatter(logFormatter)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(levelname)-5.5s] %(message)s"))
    ch.setLevel(logging.WARNING)
    if ctx.obj['DEBUG']:
        ch.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.addHandler(ch)

    ctx.obj['LOGGER'] = logger


def file_pattern_exist(dirname, pattern):
    files = [f for f in os.listdir(dirname) if os.path.isfile(f)]
    for f in files:
        if re.match(pattern, f): return True

    return False


