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

from collections import defaultdict
from base_checker import BaseChecker

class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[] # dependent checks
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        file_without_data_category = defaultdict(list)
        for fl in self.metadata.get('files'):
            if not fl.get('info') or not fl['info'].get('data_category'):
                file_without_data_category['missing'].append(fl['fileName'])
            elif not fl['info']['data_category'] == 'Sequencing Reads':
                file_without_data_category['mismatch'].append(fl['fileName'])

        if file_without_data_category:
            if 'mismatch' in file_without_data_category:
                if 'missing' in file_without_data_category:
                    message = "Field 'info.data_category' is NOT populated with 'Sequencing Reads' for " \
                        "file(s): '%s'. Field 'info.data_category' is NOT found for file(s): '%s'." \
                            % (', '.join(sorted(file_without_data_category['mismatch'])), \
                            ', '.join(sorted(file_without_data_category['missing'])))
                else:
                    message = "Field 'info.data_category' is NOT populated with 'Sequencing Reads' for " \
                        "file(s): '%s'" % ', '.join(sorted(file_without_data_category['mismatch']))
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
            else:
                message = "Field 'info.data_category' is NOT found for " \
                    "file(s): '%s'" % ', '.join(sorted(file_without_data_category['missing']))
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'WARNING'
             
        else:
            self.status = 'VALID'
            message = "Field 'info.data_category' is found populated with 'Sequencing Reads'. Validation status: VALID"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
