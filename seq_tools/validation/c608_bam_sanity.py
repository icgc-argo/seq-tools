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
from seq_tools.utils import run_cmd


class Checker(BaseChecker):
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            threads=threads,
            depends_on=[  # dependent checks
                'c180_file_uniqueness',
                'c605_all_files_accessible'
            ],
            skip=skip
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        files_in_metadata = self.metadata['files']  # check files specified in metadata

        corrupted_bam_errs = {}
        for f in files_in_metadata:
            f = f['fileName']
            if not f.endswith('.bam'):  # not a BAM, skip
                continue

            bam_file = os.path.join(self.data_dir, f)

            cmd = "samtools quickcheck %s" % bam_file

            stdout, stderr, ret_code = run_cmd(cmd)
            if ret_code != 0:
                corrupted_bam_errs[f] = stderr.strip().replace('\n', ' ')

        if corrupted_bam_errs:
            errs = []
            for f in sorted(corrupted_bam_errs):
                errs.append(corrupted_bam_errs[f])

            message = "BAM file(s) samtools quickcheck failed: %s" % \
                ', '.join(sorted(corrupted_bam_errs.keys()))

            self.status = 'INVALID'
            self.message = "%s. More information can be found in under: %s" % \
                           (message, self.logger.handlers[0].baseFilename)
            self.logger.info("[%s] %s. Additional message: %s" % (self.checker, message, '; '.join(errs)))

        else:
            self.status = 'PASS'
            message = "BAM sanity check by samtools quickcheck. Validation result: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
