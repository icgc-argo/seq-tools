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

            if read_count<1000000:
                bam=align_fastq(query_fastq[rg]['file_r1'],query_fastq[rg]['file_r2'],"tmp") \
                    if query_fastq[rg]['is_paired_end'] else \
                    align_fastq(query_fastq[rg]['file_r1'],None,"tmp")
            else:
                aligned_read_count_tracker=[0]
                list_of_subset_bams=[]
                while sum(aligned_read_count_tracker)<20000:
                    subset_fastq1,subset_fastq2=split_fastq(query_fastq[rg]['file_r1'],query_fastq[rg]['file_r2'],len(aligned_read_count_tracker))
                    subset_bam=align_fastq(subset_fastq1,subset_fastq2,"tmp_"+str(len(aligned_read_count_tracker)))
                    aligned_read_count_tracker.append(aligned_read_count(subset_bam))
                    list_of_subset_bams.append(subset_bam)
                bam=merged_bam(list_of_subset_bams)

            print(query_fastq[rg]['is_paired_end'])
            strand_orientation=determine_strandedness(bam,query_fastq[rg]['is_paired_end'])

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

def determine_strandedness(bam_file,is_paired_end):
    base_directory = os.path.dirname(os.path.abspath(__file__))
    genome_build={
            "+":base_directory+"/../resources/hg38/positive/refseq.bed",
            "-":base_directory+"/../resources/hg38/negative/refseq.bed"
              }
    if is_paired_end:
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
        orientation['1+-,1-+,2++,2--']=float(sum([orientation[key] for key in ['1+-','1-+','2++','2--']]))/float(orientation['total'])
        orientation['1++,1--,2+-,2-+']=float(sum([orientation[key] for key in ['1++','1--','2+-','2-+']]))/float(orientation['total'])
                                    
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

    print(orientation,strand_orientation)
    return strand_orientation

def fastq_test_length(fastq):
    if fastq.endswith("fastq.gz") or fastq.endswith("fq.gz"):
        cmd="cat "+fastq+" | zcat | wc -l"
    else:
        cmd="bzcat "+fastq+" | wc -l"

    count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    file_size=int(count_cmd.decode('utf-8').strip())/ 4
    
    return file_size

def align_fastq(read1,read2,bam_name):
    if read2:
        cmd="STAR --genomeDir tmp_index/ " +\
            "--runThreadN 1 "\
            "--readFilesIn  "+read1+" "+read2+" "\
            "--outFileNamePrefix "+bam_name+". "\
            "--outSAMtype BAM SortedByCoordinate "\
            "--outSAMunmapped Within "\
            "--outSAMattributes Standard "\
            "--readFilesCommand zcat"
    else:
        cmd="STAR --genomeDir tmp_index/ " +\
            "--runThreadN 1 "\
            "--readFilesIn  "+read1+" "\
            "--outFileNamePrefix "+bam_name+". "\
            "--outSAMtype BAM SortedByCoordinate "\
            "--outSAMunmapped Within "\
            "--outSAMattributes Standard "\
            "--readFilesCommand zcat"

    subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    return bam_name+".Aligned.sortedByCoord.out.bam"

def split_fastq(read1,read2,num):
    if read1.endswith("fastq.gz"):
        cmd="cat "+read1+"| zcat | head -n "+str(40000*num)+"| tail -n 40000 | gzip > tmp_"+str(num)+"_read1.fastq.gz"
    else:
        cmd="bzcat "+read1+"| head -n "+str(40000*num)+"| tail -n 40000 | gzip > tmp_"+str(num)+"_read1.fastq.gz"

    print(cmd)
    run_cmd=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    if read2 and read2.endswith("fastq.gz"):
        cmd="cat "+read2+"| zcat | head -n "+str(40000*num)+"| tail -n 40000 | gzip > tmp_"+str(num)+"_read2.fastq.gz"
    elif read2 and read2.endswith("bz2"):
        cmd="bzcat "+read2+"| head -n "+str(40000*num)+"| tail -n 40000 | gzip > tmp_"+str(num)+"_read2.fastq.gz"
    
    run_cmd=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

    if read2:
        return "tmp_"+str(num)+"_read1.fastq.gz","tmp_"+str(num)+"_read2.fastq.gz"
    else:
        return "tmp_"+str(num)+"_read1.fastq.gz",None

def aligned_read_count(subset_bam):
    cmd="samtools view -F 2816 -m 30 -c "+subset_bam
    count_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    return int(count_cmd.decode('utf-8').strip().split('\n')[0])

def merged_bam(list_of_subset_bams):
    cmd="samtools merge -f tmp.merged.bam "+" ".join(list_of_subset_bams)
    run_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    return "tmp.merged.bam"

def clean_up():
    cmd="rm -r tmp*"
    run_cmd = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

def make_index():
    base_directory = os.path.dirname(os.path.abspath(__file__))
    for cmd in [
            "mkdir -p tmp_index",
            "cat "+base_directory+"/../resources/star_chr21_index/compressed/GRCh38.chr21.fasta.gz | zcat > tmp_index/GRCh38.chr21.fasta",
            "cat "+base_directory+"/../resources/star_chr21_index/compressed/gencode.v41.annotation.chr21.gtf.gz | zcat > tmp_index/gencode.v41.annotation.chr21.gtf",
            "STAR --runMode genomeGenerate "\
            "--genomeDir tmp_index "\
            "--genomeFastaFiles tmp_index/GRCh38.chr21.fasta "\
            "--sjdbGTFfile tmp_index/gencode.v41.annotation.chr21.gtf "\
            "--sjdbOverhang 99 "
            "--genomeSAindexNbases 11"
            ]:
                subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
