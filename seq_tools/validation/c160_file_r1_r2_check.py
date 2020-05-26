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


from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        if not self.metadata.get('files'):
            message = "Missing 'files' section in the metadata JSON"
            self.logger.info(message)
            self.message = message
            self.status = 'INVALID'
            return

        fns = set()
        for rg in self.metadata.get('read_groups'):
            if 'is_paired_end' not in rg:
                message = "Required field 'is_paired_end' is not found in metadata JSON in read group: %s." % rg['submitter_read_group_id']
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if not isinstance(rg['is_paired_end'], bool):
                message = "Required field 'is_paired_end' should be Boolean type in read group: %s." % rg['submitter_read_group_id']
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if 'file_r1' not in rg or not rg['file_r1']:
                message = "Required field 'file_r1' is not found in metadata JSON in read group: %s." % rg['submitter_read_group_id']
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            if rg['is_paired_end']:
                if 'file_r2' not in rg or not rg['file_r2']:
                    message = "Required field 'file_r2' is not found in metadata JSON for paired end sequencing reads in read group: %s." % rg['submitter_read_group_id']
                    self.logger.info(message)
                    self.message = message
                    self.status = 'INVALID'
                    return
                if rg['file_r1'].endswith('.bam') and not rg['file_r1'] == rg['file_r2']:
                    message = "Fields 'file_r1' and 'file_r2' should be the same for paired end BAM sequencing reads in read group: %s." % rg['submitter_read_group_id']
                    self.logger.info(message)
                    self.message = message
                    self.status = 'INVALID'
                    return
                if not rg['file_r1'].endswith('.bam') and rg['file_r1'] == rg['file_r2']:
                    message = "Fields 'file_r1' and 'file_r2' should NOT be the same for paired end FASTQ sequencing reads in read group: %s." % rg['submitter_read_group_id']
                    self.logger.info(message)
                    self.message = message
                    self.status = 'INVALID'
                    return

            else:
                if 'file_r2' in rg and rg['file_r2']:
                    message = "Field 'file_r2' must be 'null' in metadata JSON for single end sequencing in read group: %s." % rg['submitter_read_group_id']
                    self.logger.info(message)
                    self.message = message
                    self.status = 'INVALID'
                    return

            if rg.get('file_r1'): fns.add(rg['file_r1'])
            if rg.get('file_r2'): fns.add(rg['file_r2'])

        fls = set()
        for fl in self.metadata.get('files'):
            if 'fileName' not in fl or not fl['fileName']:
                message = "Required field 'fileName' is not found in metadata JSON."
                self.logger.info(message)
                self.message = message
                self.status = 'INVALID'
                return

            fls.add(fl.get('fileName'))

        if fns - fls:
            missing_files = fns - fls
            message = "File(s) specified in 'file_r1' or 'file_r2' missed in 'files' section of the metadata JSON: %s" % ", ".join(missing_files)
            self.message = message
            self.status = 'INVALID'
            self.logger.info(message)

        else:
            self.status = 'VALID'
            message = "Fields file_r1 and file_r2 check status: VALID"
            self.message = message
            self.logger.info(message)
