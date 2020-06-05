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
"""


import os
from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    def check(self):
        if not self.metadata.get('files'):
            message = "Missing 'files' section in the metadata JSON"
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        filename_with_path = set()
        for fl in self.metadata.get('files'):
            if 'fileName' not in fl or not fl['fileName']:
                message = "Required field 'fileName' is not found in metadata JSON."
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if os.sep in fl['fileName']:
                filename_with_path.add(fl['fileName'])

        if filename_with_path:
            message = "'fileName' must NOT contain path in the 'files' section of " \
                "the metadata, offending name(s): '%s'" % ', '.join(sorted(filename_with_path))
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "No path in fileName check in 'files' section status: VALID"
            self.message = message
            self.logger.info(message)
