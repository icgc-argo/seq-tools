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
        Linda Xiang <linda.xiang@oicr.on.ca>
        Junjun Zhang <junjun.zhang@oicr.on.ca>
"""


import re
from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata, skip=False):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[  # dependent checks
                'c190_no_extra_files',
                'c210_no_path_in_filename'
            ],
            skip=skip
        )

        self._patten = r'^[A-Za-z0-9]{1}[A-Za-z0-9_\.\-]*\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        if not self.metadata.get('files'):
            message = "Missing 'files' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        filename_with_mismatch_pattern = set()
        for fl in self.metadata.get('files'):
            if 'fileName' not in fl or not fl['fileName']:
                message = "Required field 'fileName' is not found or not populated in 'files' " \
                    "section of the metadata JSON."
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            if not re.match(self._patten, fl['fileName']):
                filename_with_mismatch_pattern.add(fl['fileName'])

        if filename_with_mismatch_pattern:
            message = "'fileName' must match expected pattern '%s' in the 'files' section of the metadata, " \
                "offending name(s): '%s'" % (self._patten, ', '.join(sorted(filename_with_mismatch_pattern)))
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "'fileName' matches expected pattern '%s' in 'files' " \
                "section. Validation status: PASS" % self._patten
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
