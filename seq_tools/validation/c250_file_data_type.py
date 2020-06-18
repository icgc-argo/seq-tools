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
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[
                'c180_file_uniqueness'
            ] # dependent checks
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        file_without_data_type = []
        for fl in self.metadata.get('files'):
            if not fl.get('dataType') or not fl['dataType'] == 'Submitted Reads':
                file_without_data_type.append(fl['fileName'])

        if file_without_data_type:
            message = "All files in the 'files' section of the metadata JSON are required to " \
                "have 'dataType' field being populated with 'Submitted Reads'. " \
                "File(s) found not conforming to this requirement: '%s'." \
                % ', '.join(sorted(file_without_data_type))
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
             
        else:
            self.status = 'VALID'
            message = "Field 'dataType' is found populated with 'Submitted Reads'. Validation status: VALID"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
