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
import re
import subprocess
from base_checker import BaseChecker
from seq_tools.utils import run_cmd


class Checker(BaseChecker):
    def __init__(self, ctx, metadata,threads, skip=False):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            threads=threads,
            depends_on=[  # dependent checks
                'c180_file_uniqueness',
                'c605_all_files_accessible'
            ],
            skip=skip
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        query_fastq={}
        messages= []
        for rg in self.metadata.get("read_groups"):
            if re.findall(r'\.(fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$',rg['file_r1']) and rg['file_r1'] not in query_fastq.keys():
                query_fastq[rg['file_r1']]={}
                query_fastq[rg['file_r1']]['file_r1']=rg['file_r1']
                query_fastq[rg['file_r1']]['is_paired_end']=rg['is_paired_end']
                if rg.get("file_r2"):
                    query_fastq[rg['file_r1']]['file_r2']=rg['file_r2']

        if len(query_fastq)==0:
            self.status = 'PASS'
            message = "No FASTQ Files to check"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        for fastq in query_fastq.keys():
            test_pass,file_size,message=fastq_test_length(query_fastq[fastq]['file_r1'],self.data_dir,str(self.threads))
            if test_pass:
                query_fastq[fastq]["length_file_r1"]=file_size
            else:
                self.message = message
                self.logger.info(f'[{self.checker}] {message}')
                messages.append(message)

            test_pass,message=fastq_test_regex(query_fastq[fastq]['file_r1'],self.data_dir,str(self.threads))
            if not test_pass:
                self.message = message
                self.logger.info(f'[{self.checker}] {message}')
                messages.append(message)

            if query_fastq[fastq]['is_paired_end']:

                test_pass,file_size,message=fastq_test_length(query_fastq[fastq]['file_r2'],self.data_dir,str(self.threads))
                if test_pass:
                    query_fastq[fastq]["length_file_r2"]=file_size
                else:
                    self.message = message
                    self.logger.info(f'[{self.checker}] {message}')
                    messages.append(message)

                test_pass,message=fastq_test_regex(query_fastq[fastq]['file_r2'],self.data_dir,str(self.threads))
                if not test_pass:
                    self.message = message
                    self.logger.info(f'[{self.checker}] {message}')
                    messages.append(message)

                if query_fastq[fastq]["length_file_r2"]!=query_fastq[fastq]["length_file_r1"]:
                    message = "The FASTQ file pair '%s' and '%s' do not have matching line counts" % (query_fastq[fastq]["file_r1"],query_fastq[fastq]["file_r2"])
                    self.message = message
                    self.logger.info(f'[{self.checker}] {message}')
                    messages.append(message)

        if len(messages)>0:
            self.status = 'INVALID'
            message = "The FASTQ files failed to validate for the following reasons : %s" % ";".join(messages)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            self.status = 'PASS'
            message = "FASTQ files pass sanity check. Validation result: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

def fastq_test_length(fastq,path,threads):
    file_path=os.path.join(path,fastq)
    if fastq.endswith("fastq.gz") or fastq.endswith("fq.gz"):
        cmd="unpigz -p "+threads+" -c "+file_path+" | wc -l"
    else:
        cmd="pbzip2 -d -c -p"+threads+" "+file_path+" | wc -l"

    count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    file_size=int(count_cmd.decode('utf-8').strip())/ 4
    if int(count_cmd.decode('utf-8').strip())% 4 == 0:
        return True,file_size,""
    else:
        return False,file_size,"The FASTQ file %s line count not divisible by 4" % (fastq)

def fastq_test_regex(fastq,path,threads):
    file_path=os.path.join(path,fastq)
    if fastq.endswith("fastq.gz") or fastq.endswith("fq.gz"):
        cmd="unpigz -p "+threads+" -c "+file_path+" | head -n400000"
    else:
        cmd="pbzip2 -d -c -p"+threads+" "+file_path+" | head -n400000"

    reads_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    line_count=0
    for line_tracker,line in enumerate(reads_cmd.decode('utf-8').strip().split("\n")):

        if line_count%4==0 and not re.findall(r'^@',line):
            return False,"Line #%s within FASTQ file %s not following FASTQ format, missing '@' at the start of the line" % (line_tracker+1,fastq)
        elif line_count%4==1 and re.findall(r'[^ACTGURYKMSWBDHVN-]',line): #https://en.wikipedia.org/wiki/FASTA_format
            return False,"Unknown sequence found in Line #%s within FASTQ file %s" % (line_tracker,file_path)
        elif line_count%4==2 and not re.findall(r'^\+',line): #https://en.wikipedia.org/wiki/FASTA_format
            return False,"Line #%s within FASTQ file %s not following FASTQ format, missing '+' at start of the line" % (line_tracker+1,fastq)
        elif line_count%4==3 \
            and \
            re.findall('%r'%'[^'+r''.join([chr(phred+64) for phred in range(0,41)])+']',line) \
            and \
            re.findall('%r'%'[^'+r''.join([chr(phred+33) for phred in range(0,42)])+']',line) :
            return False,"Unknown Phred character found in Line #%s within FASTQ file %s" % (line_tracker+1,fastq)
        elif line_count==3:
            line_count=0
        else:
            line_count+=1
        
    return True,None