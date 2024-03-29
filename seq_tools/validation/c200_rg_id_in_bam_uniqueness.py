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


from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(ctx, metadata, __name__,threads, skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        rg_ids_in_bams = {}
        duplicated_ids = {}
        for rg in self.metadata.get('read_groups'):
            filename = rg['file_r1']
            if not filename.endswith('.bam'):  # skip if not a BAM
                continue

            if rg.get('read_group_id_in_bam') is None:
                continue

            if filename not in rg_ids_in_bams:
                rg_ids_in_bams[filename] = set()

            if rg['read_group_id_in_bam'] in rg_ids_in_bams[filename]:
                if filename not in duplicated_ids:
                    duplicated_ids[filename] = set()
                duplicated_ids[filename].add(rg['read_group_id_in_bam'])
            else:
                rg_ids_in_bams[filename].add(rg['read_group_id_in_bam'])

        if duplicated_ids:
            msg = []
            for k, v in duplicated_ids.items():
                msg.append("BAM %s: %s" % (k, "', '".join(sorted(v))))

            self.status = 'INVALID'
            message = "'read_group_id_in_bam' must be unique within a BAM file if populated in read_groups section, " \
                "however duplicate(s) found: %s" % '; '.join(msg)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
        else:
            self.status = 'PASS'
            message = "'read_group_id_in_bam' uniqueness check status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
