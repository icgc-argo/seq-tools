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
from xmlrpc.client import boolean
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
        query_bams={}
        for rg in self.metadata.get("read_groups"):
            if rg['file_r1'].endswith('.bam') and rg['file_r1'] not in query_bams:
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
                else:
                    query_bams[rg['file_r1']]=rg['is_paired_end']              
        
        if len(query_bams)==0:
            self.status = 'PASS'
            message = "No BAMs to check"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            for bam_file in query_bams.keys():
            
                is_paired_end=query_bams[bam_file]

                if is_paired_end:
                    filter_flag='-f 64'
                else:
                    filter_flag=''

                path_bam_file=os.path.join(self.data_dir,bam_file)
                readname_regex="^[!-?A-~]{1,254}"
                readgroup_regex="RG[a-zA-Z0-9._:\ -]*.?"
                remove_whitespace="sed 's/^[[:space:]]*//g;s/ /\t/g'"

                cmd=[
                "samtools view  -F 256 "+filter_flag+" "+path_bam_file,
                "head -n5000000",
                "egrep '"+readname_regex+"|"+readgroup_regex+"' -o",
                "paste - - ",
                "sort ",
                "uniq -c ",
                remove_whitespace+" ",
                ]
            
            
                read_records = subprocess.check_output(
                    "|".join(cmd),
                    stderr=subprocess.STDOUT,
                    shell=True
                )

                previous_readname=""
                readgroups_w_same_readname=[""]
                for readline in read_records.decode('utf-8').strip().split('\n')[:-1]:
                    readgroup=readline.split("\t")[-1]
                    readname=readline.split("\t")[1]
                    readcount=readline.split("\t")[0]

                    if int(readcount)>1:
                        self.status = 'INVALID'
                        message = "Multiple instances of read name '%s' in BAM '%s' in ReadGroup '%s'" %(readname,bam_file,readgroup)
                        self.message = message
                        self.logger.info(f'[{self.checker}] {message}')
                        offending_ids.append(message)
                    if readname==previous_readname:
                        self.status = 'INVALID'
                        readgroups_w_same_readname.append(readgroup)
                    elif readname!=previous_readname and len(readgroups_w_same_readname)>1:
                        message = "Read name '%s' in BAM '%s' detected in multiple ReadGroups :%s" % (previous_readname,bam_file,",".join(["'"+rg+"'" for rg in readgroups_w_same_readname]))
                        offending_ids.append(message)
                        previous_readname=readname
                        readgroups_w_same_readname.clear()
                        readgroups_w_same_readname.append(readgroup)
                    else:
                        previous_readname=readname
                        readgroups_w_same_readname.pop()
                        readgroups_w_same_readname.append(readgroup)

        if offending_ids:
            if len(offending_ids)>=5:
                offending_ids_cap="Too many conflicts to list .Displaying first five "
            else:
                offending_ids_cap="Following readname anomalies were detected "
            message = offending_ids_cap+": " + ";".join(offending_ids[:5])
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'PASS'
            message = "Repeated Read names within Read groups in BAM not found: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
