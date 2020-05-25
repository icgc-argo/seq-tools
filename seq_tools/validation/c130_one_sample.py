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
        if not self.metadata.get('samples'):
            message = "Missing 'samples' section in the metadata JSON"
            self.message = message
            self.status = 'INVALID'
            self.logger.info(message)
            return

        if len(self.metadata.get('samples')) != 1:
            message =  "'samples' section must contain exactly one sample in metadata, %s found" % \
                len(self.metadata.get('samples'))
            self.message = message
            self.status = 'INVALID'
            self.logger.info(message)
        else:
            message = "One and only one sample check status: VALID"
            self.status = 'VALID'
            self.message = message
            self.logger.info(message)
