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


import os
from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    def check(self):
        files_in_subdir = self.files

        if files_in_subdir is None:
            message = "No file information available in the submission " \
                "directory. This is likely a metadata only validation, " \
                "should not have invoked this checker. Please ignore."
            self.logger.info(message)
            self.message = message
            self.status = 'UNKNOWN'
            return

        files_missed_in_subdir = set()
        files_unaccessbile_in_subdir = set()

        files_in_metadata = self.metadata['files']
        for f in files_in_metadata:
            if f['fileName'] not in files_in_subdir:
                files_missed_in_subdir.add(f['fileName'])
            elif not os.access(
                    os.path.join(self.submission_directory, f['fileName']),
                    os.R_OK):
                files_unaccessbile_in_subdir.add(f['fileName'])

        if files_missed_in_subdir:
            message = "Files specified in metadata, but missed in submission directory: '%s'" % \
                ', '.join(files_missed_in_subdir)
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        if files_unaccessbile_in_subdir:
            message = "Files specified in metadata, but unaccessilbe in submission directory: '%s'" % \
                ', '.join(files_unaccessbile_in_subdir)
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        self.status = 'VALID'
        message = "All submission files accessible check: VALID"
        self.message = message
        self.logger.info(message)
