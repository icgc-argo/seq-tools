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
"""


import os
from base_checker import BaseChecker
import subprocess
import re
import sys

class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    def check(self):
        files_in_subdir = self.files

        if not files_in_subdir:
            message = "No file information available in the submission " \
                "directory. This is likely a metadata only validation, " \
                "should not have invoked this checker. Please ignore."
            self.logger.info(message)
            self.message = message
            self.status = 'Not applicable'
            return

        offending_ids = {}
        for f in files_in_subdir:
            if not os.path.basename(f).endswith('.bam'): continue
            fpath = os.path.join(self.submission_directory, os.path.basename(f))
            if not os.access(fpath, os.R_OK):
                message = "BAM file in submission directory is NOT accessible: '%s'" % os.path.basename(f)
                self.logger.info(message)
                self.message = message
                self.status = 'Not applicable'
                return
            
            # retrieve the @RG from BAM header
            try:
                header = subprocess.check_output(['samtools', 'view', '-H', fpath])
            except Exception as e:
                message = "BAM file in submission directory is NOT accessible: '%s'" % os.path.basename(f)
                self.logger.info(message)
                self.message = message
                self.status = 'Not applicable'
                return

            # get @RG
            header_array = header.decode('utf-8').rstrip().split('\n')

            for line in header_array:
                if not line.startswith("@RG"): continue
                rg_array = line.rstrip().replace('\t', '\\t')
                # get rg_id from BAM header
                rg_id_in_bam = ':'.join([ kv for kv in rg_array.split('\\t') if kv.startswith('ID:') ][0].split(':')[1:])
                if re.search(r'[,/?%*\ \$]', rg_id_in_bam):
                    if not offending_ids.get(os.path.basename(f)): 
                        offending_ids[os.path.basename(f)] = set()
                    offending_ids[os.path.basename(f)].add(rg_id_in_bam)

        if offending_ids:
            msg = []
            for k, v in offending_ids.items():
                msg.append("%s: %s" % (k, ', '.join(v)))
            
            message = "'RGID' in BAM header contains invalid character: '%s'. " % '; '.join(msg) + "Invalid characters include: whitespace, comma, $, %, ?, /, *." 
             
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'        
        else:
            self.status = 'VALID'
            message = "'RGID' in BAM header check: VALID"
            self.message = message
            self.logger.info(message)
