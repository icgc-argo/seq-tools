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
from collections import defaultdict
from base_checker import BaseChecker
from seq_tools.utils import calculate_md5
from seq_tools.utils import calculate_size

class Checker(BaseChecker):
    """
    This checker verify whether fileSize and fileMd5sum provided in metadata are correct or not. 
    """

    def __init__(self, ctx, metadata, skip=False):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
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

        files_in_metadata=[]
        for f in self.metadata['files']:
            if f.get("info") and f['info'].get("original_cram_info"):
                files_in_metadata.append(f)
        if len(files_in_metadata)==0:
            self.status = 'PASS'
            message = "No nested cram info to check: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        ### Check Md5sum 
        md5_mismatches = defaultdict(list)  # dict to keep all mismatches from all files
        for f in files_in_metadata:
            seq_file = os.path.join(self.data_dir, f['info']['original_cram_info']['fileName'])
            real_md5 = calculate_md5(seq_file)
            if not real_md5 == f['info']['original_cram_info']['fileMd5sum']:
                md5_mismatches[f['info']['original_cram_info']['fileName']].append(
                        "%s: %s vs %s" % ('fileMd5sum', real_md5, f['info']['original_cram_info']['fileMd5sum']))

        ### Check File size
        size_mismatches = defaultdict(list)  # dict to keep all mismatches from all files
        for f in files_in_metadata:
            seq_file = os.path.join(self.data_dir, f['info']['original_cram_info']['fileName'])
            real_size = calculate_size(seq_file)
            if not real_size == f['info']['original_cram_info']['fileSize']:
                size_mismatches[f['info']['original_cram_info']['fileName']].append(
                        "%s: %s vs %s" % ('fileSize', real_size, f['info']['original_cram_info']['fileSize']))

        ### Output errors
        if size_mismatches or md5_mismatches:
            mismatches_strings = []
            self.status = 'INVALID'
            for f in sorted(size_mismatches):  # file, use sorted so that order is determinastic, good for comparision in tests
                mismatches_strings.append("[%s: %s]" % (f, ", ".join(size_mismatches[f])))

            for f in sorted(md5_mismatches):  # file, use sorted so that order is determinastic, good for comparision in tests
                mismatches_strings.append("[%s: %s]" % (f, ", ".join(md5_mismatches[f])))
                
            message = "The following fields calculated from the sequencing files does NOT match " \
                "the info provided in metadata JSON. Details of the difference: %s" % "; ".join(mismatches_strings)

            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "The fileMd5sum and fileSize calculated from the sequencing files matches " \
                "the info provided in metadata JSON: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
