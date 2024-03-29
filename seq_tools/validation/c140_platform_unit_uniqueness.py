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
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(ctx, metadata, __name__,threads, skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        pus = set()
        duplicated_pus = []
        for rg in self.metadata.get('read_groups'):
            if 'platform_unit' not in rg or not rg['platform_unit'] or not isinstance(rg['platform_unit'], str):
                message = "Required field 'platform_unit' not found or not populated properly in metadata JSON"
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            if rg['platform_unit'] in pus:
                duplicated_pus.append(rg['platform_unit'])
            else:
                pus.add(rg['platform_unit'])

        if duplicated_pus:
            message = "'platform_unit' duplicated in metadata: '%s'" % \
                ', '.join(duplicated_pus)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Platform unit uniqueness check status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
