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
    def __init__(self, ctx, metadata):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[  # dependent checks
                'c110_rg_id_uniqueness',
                'c200_rg_id_in_bam_uniqueness'
            ]
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        # get submitter_read_group_ids with no read_group_id_in_bam populated
        submitter_rg_ids_alone = {}
        read_group_ids_in_bam = {}
        for rg in self.metadata.get('read_groups'):
            filename = rg['file_r1']
            if not filename.endswith('.bam'):  # skip if not a BAM
                continue

            # only interested in submitter_read_group_id check when read_group_id_in_bam is not populated
            if rg.get('read_group_id_in_bam') is None:
                if filename not in submitter_rg_ids_alone:
                    submitter_rg_ids_alone[filename] = []
                submitter_rg_ids_alone[filename].append(rg['submitter_read_group_id'])

            else:
                if filename not in read_group_ids_in_bam:
                    read_group_ids_in_bam[filename] = []
                read_group_ids_in_bam[filename].append(rg['read_group_id_in_bam'])
                continue

        offending_submitter_rg_ids = []
        for f in sorted(submitter_rg_ids_alone):
            for rg in sorted(submitter_rg_ids_alone[f]):
                if rg in read_group_ids_in_bam[f]:  # submitter_rg_id collide with rg_id_in_bam
                    offending_submitter_rg_ids.append(rg)

        if offending_submitter_rg_ids:
            self.status = 'INVALID'
            message = "For any read group, when 'read_group_id_in_bam' is not populated, 'submitter_read_group_id' must " \
                "NOT be the same as 'read_group_id_in_bam' of another read group from the same BAM file. However, " \
                "offending submitter_read_group_id(s) found: %s" % ', '.join(sorted(offending_submitter_rg_ids))
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "For any read group, when 'read_group_id_in_bam' is not populated, 'submitter_read_group_id' must " \
                "NOT be the same as 'read_group_id_in_bam' of another read group from the same BAM file. Validation " \
                "result: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
