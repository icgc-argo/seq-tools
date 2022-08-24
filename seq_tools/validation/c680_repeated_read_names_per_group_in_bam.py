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
        super().__init__(
            ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[
                "c605_all_files_accessible",
                "c608_bam_sanity",
                "c610_rg_id_in_bam",
                "c620_submitter_read_group_id_match",
                "c630_rg_id_in_bam_match",
                "c670_rg_is_paired_in_bam"
            ],
            skip=skip)

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
            if rg['file_r1'].endswith('.bam'):
                if rg['file_r1'] not in query_bams:
                    query_bams[rg['file_r1']]={}
                    query_bams[rg['file_r1']]['is_paired_end']=rg['is_paired_end']
                    query_bams[rg['file_r1']]['rg']=[]
                    query_bams[rg['file_r1']]['rg'].append(rg['read_group_id_in_bam'])
                else:
                    query_bams[rg['file_r1']]['rg'].append(rg['read_group_id_in_bam'])
                             
        
        if len(query_bams)==0:
            self.status = 'PASS'
            message = "No BAMs to check"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            for bam_file in query_bams.keys():
            
                is_paired_end=query_bams[bam_file]['is_paired_end']

                if is_paired_end:
                    filter_flag='-f 64'
                else:
                    filter_flag=''

                path_bam_file=os.path.join(self.data_dir,bam_file)

                cmd=[
                "samtools view  -F 2304 "+filter_flag+"".join([" -r "+rg.replace("'","\\'") for rg in query_bams[bam_file]['rg']])+" "+path_bam_file,
                "head -n500000"
                ]
            
            
                read_records = subprocess.check_output(
                    "|".join(cmd),
                    stderr=subprocess.STDOUT,
                    shell=True
                )

                if len(read_records.decode('utf-8').split('\n'))<=1:
                    message = "The following read groups yielded no reads to check in BAM '%s' : %s " %(bam_file,query_bams[bam_file]['rg'])
                    self.logger.info(f'[{self.checker}] {message}')
                    self.message = message
                    self.status = 'INVALID'
                    return   


                read_dict={}
                for ind,read in enumerate(read_records.decode("utf-8").strip().split("\n")[:-1]):
                    readname=re.findall(r'^[!-?A-~]{1,254}',read)[0]
                    readgroup=re.findall(r'RG[a-zA-Z0-9._:\ \-\'$]*.?',read)[0]
                    if readname in read_dict:
                        read_dict[readname]['count']+=1
                        if not readgroup in read_dict[readname]['rg']:
                            read_dict[readname]['rg'].append(readgroup)
                    else:
                        read_dict[readname]={"count":1,"rg":[readgroup]}

                for read in read_dict.keys():
                    if read_dict[read]['count']>1:
                        self.status = 'INVALID'
                        if len(read_dict[read]['rg'])>1:
                            message = "Read name '%s' in BAM '%s' detected in multiple ReadGroups :%s" % (read,bam_file,",".join(["'"+rg+"'" for rg in read_dict[read]['rg']]))
                        else:
                            message = "Multiple instances of read name '%s' in BAM '%s' in ReadGroup '%s'" %(read,bam_file,read_dict[read]['rg'][0])

                        self.message = message
                        self.logger.info(f'[{self.checker}] {message}')
                        offending_ids.append(message)

        if offending_ids:
            if len(offending_ids)>=5:
                offending_ids_cap="Too many conflicts to list. Displaying first five "
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
