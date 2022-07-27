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
        Edmund Su <linda.xiang@oicr.on.ca>
"""


import re
from base_checker import BaseChecker
import json
import requests

class Checker(BaseChecker):
    def __init__(self, ctx, metadata, skip=False):
        super().__init__(ctx, metadata, __name__, skip=skip)

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
        
        url='https://raw.githubusercontent.com/icgc-argo/argo-metadata-schemas/master/schemas/sequencing_experiment.json'
        resp=requests.get(url)
        
        if resp.status_code==200:
            regex=resp.json()['schema']['properties']['read_groups']['items']['allOf'][0]['properties']['submitter_read_group_id']['pattern']
        else:
            regex='^[a-zA-Z0-9\\-_:\\.]+$'

        offending_ids = set()
        for rg in self.metadata.get('read_groups'):
            if 'submitter_read_group_id' not in rg:
                message = "Required field 'submitter_read_group_id' not found in metadata JSON"
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return

            if not re.match(regex, rg['submitter_read_group_id']):
                offending_ids.add(rg['submitter_read_group_id'])

        if offending_ids:
            message =  "'submitter_read_group_id' in metadata contains invalid character or " \
                "is shorter then 2 characters: '%s'. " \
                "Permissible characters include: a-z, A-Z, 0-9, - (hyphen), " \
                "_ (underscore), : (colon), . (dot)" % ', '.join(offending_ids)
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Read group ID permissible character check status: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
