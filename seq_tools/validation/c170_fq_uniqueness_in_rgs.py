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

        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        fqs = set()
        duplicated_fqs = []
        for rg in self.metadata.get('read_groups'):
            if 'file_r1' not in rg:
                message = "Required field 'file_r1' not found in metadata JSON"
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            if rg['file_r1'].endswith('.bam'):
                continue

            if rg['file_r1'] in fqs:
                duplicated_fqs.append(rg['file_r1'])
            else:
                fqs.add(rg['file_r1'])

            if 'file_r2' in rg:
                if rg['file_r2'].endswith('.bam'):
                    continue
                if rg['file_r2'] in fqs:
                    duplicated_fqs.append(rg['file_r2'])
                else:
                    fqs.add(rg['file_r2'])

        if duplicated_fqs:
            message = "FASTQ file(s) duplicated in 'file_r1/file_r2' of " \
                "the 'read_groups' section in the metadata: '%s'" % \
                ', '.join(sorted(duplicated_fqs))
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "FASTQ uniqueness in read groups check status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
