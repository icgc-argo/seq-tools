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
        Linda Xiang <linda.xiang@oicr.on.ca>
"""


import os
from base_checker import BaseChecker
import subprocess


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    @BaseChecker._catch_exception
    def check(self):
        # get all RG ID from BAM(s)
        files_in_metadata = self.metadata['files']

        rg_id_in_bams = {}
        for f in files_in_metadata:
            f = f['fileName']
            if not f.endswith('.bam'):  # not a BAM, skip
                continue

            bam_file = os.path.join(self.data_dir, f)

            # retrieve the @RG from BAM header
            header = subprocess.check_output(
                ['samtools', 'view', '-H', bam_file],
                stderr=subprocess.STDOUT
            )
            header_array = header.decode('utf-8').rstrip().split('\n')

            for line in header_array:
                if not line.startswith("@RG"):
                    continue
                rg_array = line.rstrip().replace('\t', '\\t')

                # get rg_id from BAM header
                rg_id_in_bam = ':'.join([
                    kv for kv in rg_array.split('\\t') if kv.startswith('ID:')
                ][0].split(':')[1:])

                if f not in rg_id_in_bams:
                    rg_id_in_bams[f] = []

                # don't need to check rg_id uniquessness as it's checked already elsewehere earlier
                rg_id_in_bams[f].append(rg_id_in_bam)

        read_groups = self.metadata['read_groups']

        offending_ids = {}
        for rg in read_groups:
            filename = rg['file_r1']
            if not filename.endswith('.bam'):
                continue  # skip if not BAM

            rg_id_in_bam = rg.get('read_group_id_in_bam')
            if rg_id_in_bam is None:
                continue

            if rg_id_in_bam not in rg_id_in_bams.get(filename, []):
                if filename not in offending_ids:
                    offending_ids[filename] = []
                offending_ids[filename].append(rg_id_in_bam)

        if offending_ids:
            msg = []
            for k, v in offending_ids.items():
                msg.append("BAM %s: %s" % (k, ', '.join(sorted(v))))

            self.status = 'INVALID'
            message = "'read_group_id_in_bam' specified in 'read_groups' section of the metadata not found " \
                "in BAM file. Offending ID(s): %s" % '; '.join(msg)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
        else:
            self.status = 'PASS'
            message = "'read_group_id_in_bam' in metadata matches RG ID in BAM check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
