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

        all_sms = set()
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

            for line in header_array:
                if not line.startswith("@RG"):
                    continue
                rg_array = line.rstrip().replace('\t', '\\t')

                # get sm from BAM header
                sm_in_bam = ':'.join([
                    kv for kv in rg_array.split('\\t') if kv.startswith('SM:')
                ][0].split(':')[1:])

                all_sms.add(sm_in_bam)

        # this could raise exception if 'samples' does not exist in metadata, which is fine
        # earlier check (c130) should have already reported the problem
        sample = self.metadata['samples'][0]

        submitter_sample_id = sample.get('submitterSampleId')
        if submitter_sample_id is None:
            self.status = 'INVALID'
            message = "Required field 'submitterSampleId' not exists or not populated in the 'samples' section " \
                "of the metadata JSON"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        if bams and len(all_sms) != 1:
            raise Exception("No SM or more than one SM found in BAM(s): '%s'. Please see earlier check status "
                            "for details." % ', '.join(all_sms))

        elif bams and list(all_sms)[0] != submitter_sample_id:
            self.status = 'INVALID'
            message = "SM in BAM header does not match submitterSampleId in metadata JSON: %s vs %s" % \
                (list(all_sms)[0], submitter_sample_id)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "One and only one SM in @RG BAM header check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
