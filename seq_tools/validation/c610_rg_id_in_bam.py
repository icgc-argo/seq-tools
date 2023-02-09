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
import re


class Checker(BaseChecker):
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(ctx, metadata, __name__,threads, skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        # can add more ascii characters later as we verify safe to add
        re_permissible_rgid = r'^[0-9a-zA-Z-_:\'\.\+]+$'

        files_in_metadata = self.metadata['files']  # check files specified in metadata

        offending_ids = {}
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

            rg_ids = set()
            duplicated_rg_ids = set()
            for line in header_array:
                if not line.startswith("@RG"):
                    continue
                rg_array = line.rstrip().replace('\t', '\\t')

                # get rg_id from BAM header
                rg_id_in_bam = ':'.join([
                    kv for kv in rg_array.split('\\t') if kv.startswith('ID:')
                ][0].split(':')[1:])

                # check rg_id uniqueness
                if rg_id_in_bam in rg_ids:
                    duplicated_rg_ids.add(rg_id_in_bam)
                else:
                    rg_ids.add(rg_id_in_bam)

                # check permissible characters in rg_id
                if not re.search(re_permissible_rgid, rg_id_in_bam):
                    if not offending_ids.get(f):
                        offending_ids[f] = set()
                    offending_ids[f].add(rg_id_in_bam)

            if not rg_ids:
                self.status = 'INVALID'
                message = "No read group ID found in header for BAM: %s" % f
                self.message = message
                self.logger.info(f'[{self.checker}] {message}')
                return

            elif duplicated_rg_ids:
                self.status = 'INVALID'
                message = "Duplicated read group ID found: %s in BAM: %s" % \
                    (", ".join(sorted(duplicated_rg_ids)), f)
                self.message = message
                self.logger.info(f'[{self.checker}] {message}')
                return

        if offending_ids:
            msg = []
            for k, v in offending_ids.items():
                msg.append("BAM %s: %s" % (k, ', '.join(sorted(v))))

            message = "Read group ID in BAM header contains non-permissible character " \
                "(valid characters include: %s). Offending ID(s): %s" % (
                    ''.join(re_permissible_rgid[1:-2]), '; '.join(msg)
                )

            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Read group ID in BAM header check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
