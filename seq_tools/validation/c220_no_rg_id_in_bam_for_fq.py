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


from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata, skip=False):
        super().__init__(ctx, metadata, __name__, skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        offending_ids = []
        for rg in self.metadata.get('read_groups', []):
            if rg.get('read_group_id_in_bam', None) is None:
                continue
            if not rg['file_r1'].endswith('.bam'):
                offending_ids.append(rg['read_group_id_in_bam'])

        if offending_ids:
            self.status = 'INVALID'
            message = "'read_group_id_in_bam' must NOT be populated in 'read_groups' section when " \
                "it is not a BAM file: '%s'" % "', '".join(offending_ids)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
        else:
            self.status = 'PASS'
            message = "'read_group_id_in_bam' not populated for FASTQ check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
