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


from distutils import cmd
from distutils.log import error
import os
from base_checker import BaseChecker
import subprocess
import re
import json

class Checker(BaseChecker):
    def __init__(self, ctx, metadata, skip=False):
        super().__init__(
            ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[
                "c605_all_files_accessible",
                "c609_fastq_sanity",
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

        query_fastq={}
        for rg in self.metadata.get("read_groups"):
            if rg['file_r1'] not in query_fastq.keys() and (rg['file_r1'].endswith("fastq.gz") or rg['file_r1'].endswith("fq.gz") or rg['file_r1'].endswith("fastq.bz2") or rg['file_r1'].endswith("fq.bz2")):
                query_fastq[rg['file_r1']]={}
                query_fastq[rg['file_r1']]['file_r1']=os.path.join(self.data_dir,rg['file_r1'])
                query_fastq[rg['file_r1']]['is_paired_end']=rg['is_paired_end']
                query_fastq[rg['file_r1']]['library_strandedness']=self.metadata.get('experiment')['library_strandedness']
                if rg.get("file_r2"):
                    query_fastq[rg['file_r1']]['file_r2']=os.path.join(self.data_dir,rg['file_r2'])

        if len(query_fastq.keys())==0:
            self.status = 'PASS'
            message = "No FASTQs associated to RNA-Seq experiments to check : SKIPPING"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        
        problematic_fastqs=[]
        make_index()
        for rg in query_fastq.keys():
            read_count=fastq_test_length(query_fastq[rg]['file_r1'])

            if read_count>1000000:
                subset_fastq1,subset_fastq2=split_fastq(query_fastq[rg]['file_r1'],query_fastq[rg]['file_r2'],read_count)
            else:
                subset_fastq1=query_fastq[rg]['file_r1']
                subset_fastq2=query_fastq[rg]['file_r2']

            salmon_output=align_fastq(subset_fastq1,subset_fastq2) \
                    if query_fastq[rg]['is_paired_end'] else \
                    align_fastq(subset_fastq1,None)

            strand_orientation=determine_strandedness(salmon_output,query_fastq[rg]['is_paired_end'])

            clean_up()

            fastq="["+query_fastq[rg]['file_r1']+","+query_fastq[rg]['file_r2']+"]" if query_fastq[rg]['is_paired_end'] else "["+query_fastq[rg]['file_r1']+"]"
            if strand_orientation!=query_fastq[rg]['library_strandedness']:
                message =  "Strand orientation for RNA-Seq file %s detected as %s. Not matching metadata %s : INVALID"  % (fastq,strand_orientation,self.metadata.get('experiment')['library_strandedness'])
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                self.status = 'INVALID'
                problematic_fastqs.append(fastq)
            else:
                message =  "Strand orientation for RNA-Seq file %s detected as %s. Matching metadata %s : PASS"  % (fastq,strand_orientation,self.metadata.get('experiment')['library_strandedness'])
                self.logger.info(f'[{self.checker}] {message}')
                self.message = message
                                                                                                        
        if len(problematic_fastqs)>0:
            self.status = 'INVALID'
            message = "The following RNA-seq FASTQs' stand orientation does not match metadata : %s" % ",".join(problematic_fastqs)                
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return
        else:
            self.status = 'PASS'
            message = "All FASTQs strand orientation check : PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

def determine_strandedness(salmon_json,is_paired_end):
    with open(salmon_json, 'r') as f:
        data=f.read()
        salmon_dict = json.loads(data)

    convert_terms={
        "IU":"UNSTRANDED",
        "U":"UNSTRANDED",
        "ISR":"FIRST_READ_SENSE_STRAND",
        "SR":"FIRST_READ_SENSE_STRAND",
        "ISF":"FIRST_READ_ANTISENSE_STRAND",
        "SF":"FIRST_READ_ANTISENSE_STRAND",
    }
    print(convert_terms[salmon_dict['library_types'][0]])
    return convert_terms[salmon_dict['library_types'][0]]

def fastq_test_length(fastq):
    if fastq.endswith("fastq.gz") or fastq.endswith("fq.gz"):
        cmd="cat "+fastq+" | zcat | wc -l"
    else:
        cmd="cat "+fastq+" | bzcat | wc -l"

    count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    file_size=int(count_cmd.decode('utf-8').strip())/ 4
    
    return file_size

def align_fastq(read1,read2):
    if read2:
        cmd="salmon quant "\
            "-i tmp/transcript_index "\
            "-l A "\
            "-1 "+read1+" "\
            "-2 "+read2+" "\
            "--validateMappings "\
            "-o transcript_quant"
    else:
        cmd="salmon quant "\
            "-i tmp/transcript_index "\
            "-l A "\
            "-1 "+read1+" "\
            "--validateMappings "\
            "-o transcript_quant"

    subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    return "transcript_quant/aux_info/meta_info.json"

def split_fastq(read1,read2,num):
    if read1.endswith("gz"):
        cmd="cat "+read1+"| zcat | head -n "+str(0.25*num)+" | gzip > tmp/tmp_"+str(num)+"_read1.fastq.gz"
    elif read2 and read2.endswith("bz2"):
        cmd="cat "+read1+"| bzcat | head -n "+str(0.25*num)+" | gzip > tmp/tmp_"+str(num)+"_read1.fastq.gz"

    run_cmd=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    if read2 and read2.endswith("gz"):
        cmd="cat "+read2+"| zcat | head -n "+str(0.25*num)+" | gzip > tmp/tmp_"+str(num)+"_read2.fastq.gz"
    elif read2 and read2.endswith("bz2"):
        cmd="cat "+read2+"| bzcat | head -n "+str(0.25*num)+" | gzip > tmp/tmp_"+str(num)+"_read2.fastq.gz"
    
    run_cmd=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    if read2:
        return "tmp_read1.fastq.gz","tmp_read2.fastq.gz"
    else:
        return "tmp_read1.fastq.gz",None

def clean_up():
    cmd="rm -r tmp;rm -r tmp_index;rm -r transcript_quant"
    run_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

def make_index():
    base_directory = os.path.dirname(os.path.abspath(__file__))
    for cmd in [
            "mkdir -p tmp",
            "curl https://ftp.ensembl.org/pub/release-87/fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz -o tmp/Homo_sapiens.GRCh38.cdna.all.fa.gz",
            "salmon index -t tmp/Homo_sapiens.GRCh38.cdna.all.fa.gz -i tmp/transcript_index"
            ]:
                subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
