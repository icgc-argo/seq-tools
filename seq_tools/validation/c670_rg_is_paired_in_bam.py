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
        Edmund Su <edmund.su@oicr.on.ca>
"""


import os
from base_checker import BaseChecker
import subprocess
import re


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
    
            
        offending_rgs ={}
        for rg in self.metadata.get('read_groups'):
        
            if 'is_paired_end' not in rg:
                message = "Field 'is_pair_end' is not found for readgroup : %s" % rg['submitter_read_group_id']
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return
            elif rg['is_paired_end']==None:
                message = "Field 'is_pair_end' for readgroup is null. Must be boolean: %s" % rg['submitter_read_group_id']
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                return
            if not rg['file_r1'].endswith('.bam'):
                continue
            if rg['file_r1'] not in offending_rgs.keys():
                offending_rgs[rg['file_r1']]=[]

            bam_file=os.path.join(self.data_dir,rg['file_r1'])
            cmd=['samtools', 'view', '-f','128', bam_file,"|","egrep",rg['read_group_id_in_bam'].replace("'","\\'"),"-m","10","|", "wc","-l"]
            paired_check = subprocess.check_output(
                " ".join(cmd),
                stderr=subprocess.STDOUT,
                shell=True
            )
            paired_check_bool = True if "10" in paired_check.decode('utf-8').strip() else False
            paired_metadata_bool = rg['is_paired_end']
            if paired_check_bool != paired_metadata_bool:
                offending_rgs[rg['file_r1']].append(rg['submitter_read_group_id'])
                
                self.status = 'INVALID'
                message = "Read group paired status in BAM does not match field 'is_paired_end' in metadata JSON: %s" % rg['submitter_read_group_id']
                self.message = message
                self.logger.info(f'[{self.checker}] {message}')

        
        msg = []
        for rg in offending_rgs.keys():
            if len(offending_rgs[rg])>0:
                msg.append("Offending read groups in BAM %s: %s" % (rg,",".join(offending_rgs[rg])))
        if msg:    
            message = "Paired status in BAM does not match field 'is_paired_end' in metadata JSON for the following: %s" % ('; '.join(msg))
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return
        else:
            self.status = 'PASS'
            message = "Read group pair status in BAM check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return