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
"""


import os
from collections import defaultdict
from base_checker import BaseChecker
from seq_tools.utils import run_cmd


field_mapping = [
    ['BC', 'rg', 'sample_barcode'],
    ['CN', 'experiment', 'sequencing_center'],
    ['DT', 'experiment', 'sequencing_date'],
    ['LB', 'rg', 'library_name'],
    ['PI', 'rg', 'insert_size'],
    ['PL', 'experiment', 'platform'],
    ['PM', 'experiment', 'platform_model'],
    ['PU', 'rg', 'platform_unit']
]


class Checker(BaseChecker):
    """
    This checker compares information in BAM @RG header with what's in metadata,  specifically
    the following fields:
        BC=sample_barcode
        CN=sequencing_center
        DT=sequencing_date
        LB=library_name
        PI=insert_size
        PL=platform
        PM=platform_model
        PU=platform_unit

    Any mismatch will be reported as WARNING, information in metadata will take precedence to be
    kept while information in original submitted BAM will be lost eventually
    """

    def __init__(self, ctx, metadata):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[  # dependent checks
                'c110_rg_id_uniqueness',
                'c160_file_r1_r2_check',
                'c200_rg_id_in_bam_uniqueness',
                'c240_submitter_rg_id_collide_with_rg_id_in_bam',
                'c180_file_uniqueness',
                'c605_all_files_accessible',
                'c610_rg_id_in_bam',
                'c620_submitter_read_group_id_match'
            ]
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        files_in_metadata = self.metadata['files']

        # first get metadata from BAM @RG header
        all_rgs = {}  # dict to keep all read groups from all BAMs
        for f in files_in_metadata:
            f = f['fileName']
            if not f.endswith('.bam'):  # not a BAM, skip
                continue

            bam_file = os.path.join(self.data_dir, f)

            # retrieve the @RG from BAM header
            cmd = "samtools view -H %s" % bam_file
            header, stderr, ret_code = run_cmd(cmd)

            header_array = header.rstrip().split('\n')

            rgs_in_bam = {}
            for line in header_array:
                if not line.startswith("@RG"):
                    continue

                rg = {}
                for kv in line.split('\t'):
                    if ':' not in kv:  # like '@RG'
                        continue
                    k, v = kv.split(':')[0], ':'.join(kv.split(':')[1:])
                    rg[k] = v

                # all RG IDs from one BAM must be unique, this has been checked in c610_rg_id_in_bam
                rgs_in_bam[rg['ID']] = rg

            all_rgs[f] = rgs_in_bam

        # now comparing read group info in metadata with all_rgs from BAM header collected above
        mismatches = defaultdict(dict)
        for rg in self.metadata['read_groups']:
            seq_file = rg['file_r1']
            if not seq_file.endswith('.bam'):  # skip if not BAM
                continue

            read_group_id = rg['submitter_read_group_id']
            if rg.get('read_group_id_in_bam'):
                read_group_id = rg['read_group_id_in_bam']

            for m in field_mapping:
                field_in_bam, ex_or_rg, field_in_meta = m

                value_in_bam = all_rgs.get(seq_file, {}).get(read_group_id, {}).get(field_in_bam)
                if ex_or_rg == 'rg':
                    value_in_meta = rg.get(field_in_meta)
                elif ex_or_rg == 'experiment':
                    value_in_meta = self.metadata['experiment'][field_in_meta]

                if value_in_bam and value_in_bam != value_in_meta:
                    if mismatches.get(seq_file, {}).get(read_group_id) is None:
                        mismatches[seq_file][read_group_id] = []

                    mismatches[seq_file][read_group_id].append(
                        "%s: %s vs %s" % (field_in_bam, value_in_bam, value_in_meta)
                    )
                elif value_in_bam:  # matches
                    self.logger.info("[%s] BAM: %s, RG: %s, field: %s, value: %s matches what is in metadata." %
                                     (self.checker, seq_file, read_group_id, field_in_bam, value_in_bam))

        if mismatches:
            mismatches_strings = []
            for f in sorted(mismatches):  # file, use sorted so that order is determinastic, good for comparision in tests
                for rg in sorted(mismatches[f]):  # rg
                    mismatches_strings.append("[BAM %s @RG %s: (%s)]" % (f, rg, ", ".join(mismatches[f][rg])))

            self.status = 'WARNING'
            message = "Information (excluding ID and SM which are validated elsewhere) in BAM @RG header does NOT match " \
                "experiment/read group info in metadata JSON. NOTE that information is the metadata JSON document will be " \
                "kept and used in ICGC ARGO uniform analysis while unmatched info in BAM header will be lost. Details of " \
                "the difference: %s" % "; ".join(mismatches_strings)

            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "Information (excluding ID and SM which are validated elsewhere) in BAM @RG header match " \
                "experiment/read group info in metadata JSON: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
