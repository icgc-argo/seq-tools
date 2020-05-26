# -*- coding: utf-8 -*-

"""
    Copyright (c) 2020, Ontario Institute for Cancer Research (OICR).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Authors:
        Junjun Zhang <junjun.zhang@oicr.on.ca>
"""


import os
import re
import logging
import datetime


def initialize_log(ctx, dir):
    logger = logging.getLogger('seq_tools: %s' % dir)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s")

    logger.setLevel(logging.INFO)

    if dir:
        log_directory = os.path.join(dir, "logs")
        log_file = "%s.log" % re.sub(r'[-:.]', '_', datetime.datetime.utcnow().isoformat())
        ctx.obj['log_file'] = log_file
        log_file = os.path.join(log_directory, log_file)

        if not os.path.isdir(log_directory):
            os.mkdir(log_directory)

        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)  # always set fh to debug
        fh.setFormatter(logFormatter)
        logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(levelname)-5.5s] %(message)s"))
    ch.setLevel(logging.WARNING)
    if ctx.obj['DEBUG']:
        ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

    ctx.obj['LOGGER'] = logger


def file_pattern_exist(dirname, pattern):
    files = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname,f))]
    for f in files:
        if re.match(pattern, f): return True

    return False


def find_files(dirname, pattern):
    files = [f for f in os.listdir(dirname)
             if (os.path.isfile(os.path.join(dirname, f)) or
                 os.path.islink(os.path.join(dirname, f)))
             ]
    files_found = []
    for f in files:
        if re.match(pattern, f):
            files_found.append(f)

    return files_found


def ntcnow_iso() -> str:
    return datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
