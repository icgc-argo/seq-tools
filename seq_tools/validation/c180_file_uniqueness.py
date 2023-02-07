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


from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(ctx, metadata, __name__,threads, skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        if not self.metadata.get('files'):
            message = "Missing 'files' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        fns = set()
        duplicated_fns = set()
        for fl in self.metadata.get('files'):
            if 'fileName' not in fl or not fl['fileName']:
                message = "Required field 'fileName' is not found in metadata JSON."
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            if fl['fileName'] in fns:
                duplicated_fns.add(fl['fileName'])
            else:
                fns.add(fl['fileName'])

        if duplicated_fns:
            message = "File(s) duplicated in 'fileName' of " \
                "the 'files' section in the metadata: '%s'" % \
                ', '.join(duplicated_fns)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Files uniqueness check in files section status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
