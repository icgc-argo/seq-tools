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


import re
from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        offending_ids = set()
        for rg in self.metadata.get('read_groups'):
            if 'submitter_read_group_id' not in rg:
                message = "Required field 'submitter_read_group_id' not found in metadata JSON"
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if not re.match(r'^[a-zA-Z0-9_\.\-]{2,}$', rg['submitter_read_group_id']):
                offending_ids.add(rg['submitter_read_group_id'])

        if offending_ids:
            message =  "'submitter_read_group_id' in metadata contains invalid character or " \
                "is shorter then 2 characters: '%s'. " \
                "Permissible characters include: a-z, A-Z, 0-9, - (hyphen), " \
                "_ (underscore) and . (dot)" % ', '.join(offending_ids)
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "Read group ID permissible character check status: VALID"
            self.message = message
            self.logger.info(message)
