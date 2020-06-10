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
import json
from click import echo
import logging
import datetime
import requests
from packaging import version
from seq_tools import __version__ as current_ver


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


def get_latest_releases():
    github_url = "https://api.github.com/repos/icgc-argo/seq-tools/releases"

    latest_releases = {
        'stable': None,
        'prerelease': None
    }

    try:
        res = requests.get(github_url, headers={'Accept': 'application/vnd.github.v3.text-match+json'})
        json_response = res.json()
    except Exception:
        echo("INFO: Unable to check for update of 'seq-tools'. Please verify Internet connection.", err=True)
        return latest_releases

    if isinstance(json_response, dict):
        if 'rate limit exceeded' in json.dumps(json_response):
            echo("INFO: Unable to check for update of 'seq-tools'. Github API rate limit exceeded.", err=True)
            pass
        return latest_releases

    for r in json_response:  # releases are ordered in reverse chronological way
        if latest_releases['prerelease'] and latest_releases['stable']:  # already found them
            break

        if r.get('prerelease'):
            if not latest_releases['prerelease']:  # get the latest prerelease
                latest_releases['prerelease'] = r.get('tag_name')
        else:
            if not latest_releases['stable']:  # get the latest stable release
                latest_releases['stable'] = r.get('tag_name')

    return latest_releases


def check_for_update(ctx, ignore_update, check_prerelease):
    # check for latest releases
    latest_releases = get_latest_releases()
    stable_release = latest_releases.get('stable')
    prerelease = latest_releases.get('prerelease')

    # there is a newer stable release
    if stable_release and version.parse(stable_release) > version.parse(current_ver):
        echo(
            "INFO: A new stable version of 'seq-tools' is available: %s, current version: %s" %
            (stable_release, current_ver), err=True)

        if ignore_update:
            echo("Ignore available update, keep using the current version.\n", err=True)
        else:
            echo(
                "Please install it by running: "
                "pip install git+https://github.com/icgc-argo/seq-tools.git@%s\n"
                "Or use --ignore-update option to continue with the current version." % stable_release,
                err=True)
            ctx.abort()

    # when set to check prerelease, no newer stable release, but newer prerelease
    elif not ignore_update and check_prerelease \
            and prerelease and version.parse(prerelease) > version.parse(current_ver):
        echo(
            "INFO: A new pre-release version of 'seq-tools' is available: %s, current version: %s\n"
            "To install the pre-release version run: "
            "pip install git+https://github.com/icgc-argo/seq-tools.git@%s\n" %
            (prerelease, current_ver, prerelease), err=True)
