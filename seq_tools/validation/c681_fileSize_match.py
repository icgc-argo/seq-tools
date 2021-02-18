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
from collections import defaultdict
from base_checker import BaseChecker
from seq_tools.utils import calculate_size


class Checker(BaseChecker):
    """
    This checker verify whether fileSize and fileMd5sum provided in metadata are correct or not. 
    """

    def __init__(self, ctx, metadata):
        super().__init__(
            ctx=ctx,
            metadata=metadata,
            checker_name=__name__,
            depends_on=[  # dependent checks
                'c180_file_uniqueness',
                'c605_all_files_accessible'
            ]
        )

    @BaseChecker._catch_exception
    def check(self):
        # status already set at initiation
        if self.status:
            return

        files_in_metadata = self.metadata['files']

        mismatches = defaultdict(list)  # dict to keep all mismatches from all files
        for f in files_in_metadata:
            seq_file = os.path.join(self.data_dir, f['fileName'])
            real_size = calculate_size(seq_file)
            if not real_size == f['fileSize']:
                mismatches[f['fileName']].append(
                        "%s: %s vs %s" % ('fileSize', real_size, f['fileSize']))

        if mismatches:
            mismatches_strings = []
            for f in sorted(mismatches):  # file, use sorted so that order is determinastic, good for comparision in tests
                mismatches_strings.append("[%s: %s]" % (f, ", ".join(mismatches[f])))

            self.status = 'INVALID'
            message = "The fileSize calculated from the sequencing files does NOT match " \
                "the info provided in metadata JSON. Details of the difference: %s" % "; ".join(mismatches_strings)

            self.logger.info(f'[{self.checker}] {message}')
            self.message = message

        else:
            self.status = 'PASS'
            message = "The fileSize calculated from the sequencing files matches " \
                "the info provided in metadata JSON: PASS"
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
