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
import subprocess
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


def run_cmd(cmd):
    p = subprocess.Popen(
        [cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    stdout, stderr = p.communicate()

    return stdout.decode("utf-8"), stderr.decode("utf-8"), p.returncode


def base_estimate(seq_file, logger, checker) -> int:
    if seq_file.endswith('.bam'):
        # get total read count
        cmd = "samtools flagstat %s" % seq_file
        bam_stats, stderr, returncode = run_cmd(cmd)

        if returncode != 0:
            raise Exception(
                "Execution of samtools flagstat on BAM: %s returned non-zero code: %s. Stderr: %s" %
                (seq_file, returncode, stderr))

        total_line = [l for l in bam_stats.rstrip().split('\n') if ' in total ' in l]

        if len(total_line) != 1:
            raise Exception(
                "Unable to parse samtools flagstat output to find total number of reads in BAM: %s" % seq_file)
        else:
            m = re.match(r'^(\d+) \+ (\d+) in total .+', total_line[0])
            if m:
                reads_qc_pass = int(m.group(1))
                reads_qc_fail = int(m.group(2))
                logger.info("[%s] Count of QC passed reads: %s, used for estimating sequencing coverage." %
                            (checker, reads_qc_pass))
                logger.info("[%s] Count of QC failed reads: %s, not used for estimating sequencing coverage." %
                            (checker, reads_qc_fail))
            else:
                raise Exception(
                    "Unable to parse samtools flagstat output to find total number of QC passed / failed reads "
                    "in BAM: %s" % seq_file)

        # guesstimate read length by pull out first 5000 QC passed reads from each end and check their lengths
        # first end reads
        cmd = "samtools view -f 0x40 -F 0x200 %s | head -%s" % (seq_file, 5000)
        reads, stderr, returncode = run_cmd(cmd)
        read_lengths = [len(r.split('\t')[9]) for r in reads.rstrip().split('\n')]
        f_average_len = sum(read_lengths) / len(read_lengths)

        # second end reads
        cmd = "samtools view -f 0x80 -F 0x200 %s | head -%s" % (seq_file, 5000)
        reads, stderr, returncode = run_cmd(cmd)
        read_lengths = [len(r.split('\t')[9]) for r in reads.rstrip().split('\n')]
        s_average_len = sum(read_lengths) / len(read_lengths)

        read_length = (f_average_len + s_average_len) / 2

        return int(reads_qc_pass * read_length)

    else:
        # retrieve first 5000 reads, get average read length, create gz or bz2 compressed tmp file and get its size
        # comparing ths size with original file size to estimate total number of reads
        pass

    return 0
