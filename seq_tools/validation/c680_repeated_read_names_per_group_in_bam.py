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
    
            
        offending_ids = []
        query_bams=\
        list(
            set(
                [rg['file_r1'] for rg in self.metadata.get('read_groups') if rg['file_r1'].endswith('.bam')]
            )
        )
        
        if len(query_bams)==0:
            self.status = 'PASS'
            message = "No BAMs to check"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            for bam_file in query_bams:
            
                path_bam_file=os.path.join(self.data_dir,bam_file)
                readname_regex="^[!-?A-~]{1,254}"
                readgroup_regex="RG[a-zA-Z0-9._:\ -]*?"
                remove_whitespace="sed 's/^[[:space:]]*//g;s/ /\\t/g'"
                filter_entries="awk '$1>2'"
            
                cmd=[
                "samtools view  -F 256 "+path_bam_file,
                "egrep '"+readname_regex+"||"+readgroup_regex+"' -o",
                "paste - - ",
                "sort ",
                "uniq -c ",
                remove_whitespace+" ",
                filter_entries,
                "cut -f2 -d' '"
                ]
            
            
                reads_check = subprocess.check_output(
                    "|".join(cmd),
                    stderr=subprocess.STDOUT,
                    shell=True
                )
                output_reads_check =reads_check.decode('utf-8').split('\n')

                if len(output_reads_check) > 1:
                    self.status = 'INVALID'
                    
                    for readline in output_reads_check[:-1]:
                        readgroup=readline.split("\t")[-1]
                        readname=readline.split("\t")[1]
                        message = "The following read names conflict in BAM %s : %s in RG %s" %(bam_file,readname,readgroup)
                        self.message = message
                        self.logger.info(f'[{self.checker}] {message}')
                        offending_ids.append(readname)
                    
                    return

        if offending_ids:
            msg = []
            for k in offending_ids:
                msg.append("The following read name appears multiple times" % (k))

            message = "Please verify read names" % ('; '.join(msg))

            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Repeated Read names within Read groups in BAM not found: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
