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

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
            return

        if not self.metadata.get('read_group_count'):
            message = "Missing 'read_group_count' field in the metadata JSON"
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
            return

        if len(self.metadata.get('read_groups')) != self.metadata.get('read_group_count'):
            message =  "The total number of read groups in 'read_groups' section is %s. It does NOT match the number specified in read_group_count: %s." % \
                (len(self.metadata.get('read_groups')), self.metadata.get('read_group_count'))
            self.message = message
            self.status = 'INVALID'
            self.logger.error(message)

        else:
            self.status = 'VALID'
            message = "Read groups count check status: VALID"
            self.message = message
            self.logger.info(message)
