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
        super().__init__(ctx, metadata, __name__)

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' in the metadata JSON"
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        rg_ids = set()
        duplicated_ids = []
        for rg in self.metadata.get('read_groups'):
            if 'submitter_read_group_id' not in rg:
                message = "Required field 'submitter_read_group_id' not found in metadata JSON"
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if rg['submitter_read_group_id'] in rg_ids:
                duplicated_ids.append(rg['submitter_read_group_id'])
            else:
                rg_ids.add(rg['submitter_read_group_id'])

        if duplicated_ids:
            message = "'submitter_read_group_id' duplicated in metadata: '%s'" % \
                ', '.join(duplicated_ids)
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "Read group ID uniqueness check status: VALID"
            self.message = message
            self.logger.info(message)
