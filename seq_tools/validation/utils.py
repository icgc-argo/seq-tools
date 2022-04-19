
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
        Linda Xiang <linda.xiang@oicr.on.ca>
        Edmund Su <linda.xiang@oicr.on.ca>
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
import hashlib


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


def check_for_update(ctx, ignore_update, check_prerelease=False):
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
    reads_to_sample = 20000

    if seq_file.endswith('.bam'):
        file_size = os.path.getsize(seq_file)

        # guesstimate read length by pull out first 'reads_to_sample' (minus header line count) QC passed reads
        # from each end and check their lengths
        # first end reads
        cmd = "samtools view -h -f 0x40 -F 0x200 %s | head -%s | tee /dev/stderr | samtools view -bS - | wc -c" \
            % (seq_file, reads_to_sample)
        portion_size_r1, reads, returncode = run_cmd(cmd)

        read_lengths_r1 = [len(r.split('\t')[9]) for r in reads.rstrip().split('\n') if not r.startswith('@')]
        average_len_r1 = int(sum(read_lengths_r1) / len(read_lengths_r1))
        logger.info("[%s] Average lenght of reads from first end: %s, from first %s reads in BAM: %s." %
                    (checker, average_len_r1, len(read_lengths_r1), seq_file))

        average_read_length = average_len_r1
        estimated_read_count = len(read_lengths_r1) * file_size / int(portion_size_r1)

        # second end reads QC passed
        cmd = "samtools view -h -f 0x80 -F 0x200 %s | head -%s | tee /dev/stderr | samtools view -bS - | wc -c" \
            % (seq_file, reads_to_sample)
        portion_size_r2, reads, returncode = run_cmd(cmd)
        read_lengths_r2 = [len(r.split('\t')[9]) for r in reads.rstrip().split('\n') if not r.startswith('@')]

        if len(read_lengths_r2):  # paired end sequencing
            average_len_r2 = int(sum(read_lengths_r2) / len(read_lengths_r2))
            logger.info("[%s] Average lenght of reads from second end: %s, from first %s reads in BAM: %s." %
                        (checker, average_len_r2, len(read_lengths_r2), seq_file))

            average_read_length = (average_len_r1 + average_len_r2) / 2

            estimated_read_count = (len(read_lengths_r1) + len(read_lengths_r2)) * file_size / \
                (int(portion_size_r1) + int(portion_size_r2))

        return int(estimated_read_count * average_read_length)

    else:
        # retrieve first 'reads_to_sample' reads, get average read length, create gz or bz2 compressed tmp file and get its size
        # comparing ths size with original file size to estimate total number of reads
        if seq_file.endswith('.bz2'):
            compression_tool = ('bzip2', 'bunzip2')
        elif seq_file.endswith('.gz'):
            compression_tool = ('gzip', 'gunzip')
        else:
            raise Exception("Unspported file format for FASTQ, file: %s" % seq_file)

        cmd = "%s -c %s | head -%s | tee /dev/stderr | %s - | wc -c" % (
            compression_tool[1], seq_file, 4 * reads_to_sample, compression_tool[0])

        portion_size, reads, ret_code = run_cmd(cmd)

        line_count = 0
        read_lengths = []
        for line in reads.rstrip().split('\n'):
            line_count += 1
            if (line_count + 2) % 4 == 0:
                read_lengths.append(len(line))

        average_len = int(sum(read_lengths) / len(read_lengths))
        if len(read_lengths) < reads_to_sample:  # we've got all the reads
            logger.info("[%s] Average lenght of reads: %s, from %s reads in FASTQ: %s." %
                        (checker, average_len, len(read_lengths), seq_file))
            return sum(read_lengths)

        else:
            logger.info("[%s] Average lenght of reads: %s, from first %s reads in FASTQ: %s." %
                        (checker, average_len, len(read_lengths), seq_file))

            file_size = os.path.getsize(seq_file)
            estimated_read_count = len(read_lengths) * file_size / int(portion_size)

            logger.info("[%s] Estimated read count: %s for FASTQ: %s." %
                        (checker, estimated_read_count, seq_file))

            return estimated_read_count * average_len


def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()

def return_genomeBuild(file_path):
    base_directory = os.path.dirname(os.path.abspath(__file__))
    
    cmd="samtools view -H "+file_path
    
    chr_process = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    chr_result=[line for line in chr_process.decode('utf-8').rstrip().split("\n") if re.findall(r'SN:1\t|SN:chr1\t|SN:Chr1\t|SN:CHR1',line)]
    chr_size=chr_result[0].replace("\t",":").split(":")[-1]
    chr_anno=chr_result[0].replace("\t",":").split(":")[2]
    
    if chr_size=='248956422':
        build={
            "+":base_directory+"/resources/hg38/positive/refseq.bed",
            "-":base_directory+"/resources/hg38/negative/refseq.bed"
              }
    elif chr_size=='249250621' and chr_anno.lower()=='chr1':
        build={
            "+":base_directory+"/resources/hg19_chr/positive/refseq.bed",
            "-":base_directory+"/resources/hg19_chr/negative/refseq.bed"
              }
    else:
        build={
            "+":base_directory+"/resources/hg19/positive/refseq.bed",
            "-":base_directory+"/resources/hg19/negative/refseq.bed"
              }

    return build
    

def index_file(file_path):
    if not os.path.exists(file_path+".bai"):
        cmd="samtools index "+file_path
        subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    return
    
