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

        sm_in_bams = {}
        bams = set()
        for f in files_in_metadata:
            f = f['fileName']
            if not f.endswith('.bam'):  # not a BAM, skip
                continue

            bams.add(f)
            bam_file = os.path.join(self.data_dir, f)

            # retrieve the @RG from BAM header
            header = subprocess.check_output(
                ['samtools', 'view', '-H', bam_file],
                stderr=subprocess.STDOUT
            )
            header_array = header.decode('utf-8').rstrip().split('\n')

            if f not in sm_in_bams:
                sm_in_bams[f] = set()

            for line in header_array:
                if not line.startswith("@RG"):
                    continue
                rg_array = line.rstrip().replace('\t', '\\t')

                # get sm from BAM header
                sm_in_bam = ':'.join([
                    kv for kv in rg_array.split('\\t') if kv.startswith('SM:')
                ][0].split(':')[1:])

                sm_in_bams[f].add(sm_in_bam)

        offending_bams = {}
        all_sms = set()
        for bam in sm_in_bams:
            all_sms.update(sm_in_bams[bam])
            if len(sm_in_bams[bam]) != 1:
                offending_bams[bam] = sm_in_bams[bam]

        # even individual BAMs are fine with one SM, but they may have different SMs
        # in such case every BAM is an offending BAM
        if not offending_bams and len(all_sms) > 1:
            offending_bams = sm_in_bams

        if bams and len(all_sms) == 0:
            self.status = 'INVALID'
            message = "No SM found in @RG BAM header, BAM(s): %s" % ', '.join(bams)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')

        elif offending_bams:
            msg = []
            for k, v in offending_bams.items():
                msg.append("BAM %s: '%s'" % (k, "', '".join(sorted(v))))

            self.status = 'INVALID'
            message = "SM in @RG headers of all BAM(s) must be populated with the same value. BAM(s) with no SM " \
                "or multiple SMs, or different SMs from different BAMs are found: %s" % '; '.join(msg)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "One and only one SM in @RG BAM header check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
