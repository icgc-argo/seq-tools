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
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    @BaseChecker._catch_exception
    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        rg_ids_in_bam = set()
        duplicated_ids = []
        for rg in self.metadata.get('read_groups'):
            if rg.get('read_group_id_in_bam', None) is None: 
                continue
            if rg['read_group_id_in_bam'] in rg_ids_in_bam:
                duplicated_ids.append(rg['read_group_id_in_bam'])
            else:
                rg_ids_in_bam.add(rg['read_group_id_in_bam'])

        if duplicated_ids:
            message = "'read_group_id_in_bam' must be unique if populated in read_groups section, however duplicate(s) found: '%s'" % \
                ', '.join(duplicated_ids)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "'read_group_id_in_bam' uniqueness check status: VALID"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
