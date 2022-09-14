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
from seq_tools.utils import return_genomeBuild ,index_file


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
                "c670_rg_is_paired_in_bam",
                "c680_repeated_read_names_per_group_in_bam"
            ],
            skip=skip)

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return
        
        if "experimental_strategy" not in self.metadata.get('experiment'):
            message = "Missing 'experimental_strategy' within 'experiment' section in the metadata JSON"
            self.logger.info(f'[{self.checker}] {message}')
            self.message = message
            self.status = 'INVALID'
            return
        elif self.metadata.get('experiment')['experimental_strategy']!='RNA-Seq':
            self.status = 'PASS'
            message = "No RNA-Seq experiments to check : SKIPPING"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        if 'library_strandedness' not in self.metadata.get('experiment'):
            self.status = 'INVALID'
            message = "RNA-Seq Library strandedness not specified"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
                                               
        query_bams=\
        list(
            set(
                [rg['file_r1'] for rg in self.metadata.get('read_groups') if rg['file_r1'].endswith('.bam')]
            )
        )
        query_bams={}
        for rg in self.metadata.get("read_groups"):
            if rg['file_r1'].endswith('.bam'):
                if rg['file_r1'] not in query_bams:
                    query_bams[rg['file_r1']]={}
                    query_bams[rg['file_r1']]['is_paired_end']=rg['is_paired_end']


        if len(query_bams)==0:
            self.status = 'PASS'
            message = "No BAM Files to check"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            problematic_bams=[]
            for bam in query_bams.keys():
                bam_file=os.path.join(self.data_dir,bam)
                index_file(bam_file)                               
                genome_build=return_genomeBuild(bam_file)
                

                if query_bams[bam]['is_paired_end']:
                    query_flags={
                    "1+":"-F 2832 -f 64",
                    "1-":"-F 2816 -f 80",
                    "2+":"-F 2832 -f 128",
                    "2-":"-F 2816 -f 144"
                    }                
                    orientation={}
                    for query in ['1++','1--','2+-','2-+','1+-','1-+','2++','2--']:

                        cmd="samtools view -m 30 -c "+bam_file+" "+query_flags[query[:2]]+" -L "+genome_build[query[-1]]
                        
                        count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
                        orientation[query]=int(count_cmd.decode('utf-8').strip().split('\n')[0])
                                                
                    orientation['total']=sum(orientation.values())                             
                    orientation['1+-,1-+,2++,2--']=sum([orientation[key] for key in ['1+-','1-+','2++','2--']])/orientation['total']
                    orientation['1++,1--,2+-,2-+']=sum([orientation[key] for key in ['1++','1--','2+-','2-+']])/orientation['total']
                                                
                    if (orientation['1+-,1-+,2++,2--']>0.6) and (orientation['1+-,1-+,2++,2--']>orientation['1++,1--,2+-,2-+']):
                        strand_orientation='FIRST_READ_ANTISENSE_STRAND'
                    elif (orientation['1++,1--,2+-,2-+']>0.6) and (orientation['1++,1--,2+-,2-+']>orientation['1+-,1-+,2++,2--']):
                        strand_orientation='FIRST_READ_SENSE_STRAND'
                    else:
                        strand_orientation='UNSTRANDED'
                else:
                    query_flags={
                    "1+":"-F 2832",
                    "1-":"-F 2816 -f 80",
                    }                
                    orientation={}
                    for query in ['1++','1--','1+-','1-+']:

                        cmd="samtools view -m 30 -c "+bam_file+" "+query_flags[query[:2]]+" -L "+genome_build[query[-1]]
                        
                        count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
                        orientation[query]=int(count_cmd.decode('utf-8').strip().split('\n')[0])
                                                
                    orientation['total']=sum(orientation.values())                             
                    orientation['1+-,1-+']=sum([orientation[key] for key in ['1+-','1-+']])/orientation['total']
                    orientation['1++,1--']=sum([orientation[key] for key in ['1++','1--']])/orientation['total']
                                                
                    if (orientation['1+-,1-+']>0.6) and (orientation['1+-,1-+']>orientation['1++,1--']):
                        strand_orientation='FIRST_READ_ANTISENSE_STRAND'
                    elif (orientation['1++,1--']>0.6) and (orientation['1++,1--']>orientation['1+-,1-+']):
                        strand_orientation='FIRST_READ_SENSE_STRAND'
                    else:
                        strand_orientation='UNSTRANDED'               
                                                                                                     
                if strand_orientation!=self.metadata.get('experiment')['library_strandedness']:
                    message =  "Strand orientation for RNA-Seq file %s detected as %s. Not matching metadata %s : INVALID"  % (bam,strand_orientation,self.metadata.get('experiment')['library_strandedness'])
                    self.logger.info(f'[{self.checker}] {message}')
                    self.message = message
                    self.status = 'INVALID'
                    problematic_bams.append(bam)
                else:
                    message =  "Strand orientation for RNA-Seq file %s detected as %s. Matching metadata %s : PASS"  % (bam,strand_orientation,self.metadata.get('experiment')['library_strandedness'])
                    self.logger.info(f'[{self.checker}] {message}')
                    self.message = message
                                                                                                     
        if len(problematic_bams)>0:
            self.status = 'INVALID'
            message = "The following RNA-seq BAMs' stand orientation does not match metadata : %s" % ",".join(problematic_bams)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            self.status = 'PASS'
            message = "All BAMs strand orientation check : PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return