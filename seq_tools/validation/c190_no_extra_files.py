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

    @BaseChecker._catch_exception
    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        if not self.metadata.get('files'):
            message = "Missing 'files' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return

        fns = set()
        for rg in self.metadata.get('read_groups'):
            if rg.get('file_r1'):
                fns.add(rg['file_r1'])
            if rg.get('file_r2'):
                fns.add(rg['file_r2'])

        fls = set()
        for fl in self.metadata.get('files'):
            if 'fileName' not in fl or not fl['fileName']:
                message = "Required field 'fileName' not populated in 'files' " \
                    "section of the metadata JSON."
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            fls.add(fl.get('fileName'))

        extra_files = fls - fns
        if extra_files:
            message = "Found extra files specified in 'files' section of the metadata JSON, " \
                "please remove unneeded files: %s from the 'files' section of the metadata JSON" % ", ".join(extra_files)
            self.message = message
            self.status = 'INVALID'
            self.logger.info(f'[{self.checker}] {message}')

        else:
            self.status = 'PASS'
            message = "No extra files check status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
