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
from base_checker import BaseChecker
from seq_tools.utils import base_estimate


COVERAGE_THRESHOLD = {
    "WGS": {
        "WARNING": 25,
        "MINIMUM": 20,
        "GENOME_SIZE": 3_000_000_000
    },
    "WXS": {
        "WARNING": 100,
        "MINIMUM": 75,
        "GENOME_SIZE": 30_000_000
    }
}


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata, __name__)

    @BaseChecker._catch_exception
    def check(self):
        files_in_metadata = self.metadata['files']

        experimental_strategy = self.metadata.get('experiment', {}).get('experimental_strategy')
        if not experimental_strategy:
            self.status = 'INVALID'
            message = "Missing required field 'experimental_strategy' under 'experiment' section in the metadata."
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        if experimental_strategy not in COVERAGE_THRESHOLD:
            self.status = 'VALID'
            message = "Sequencing coverage verification, no threshold set for %s. Validation result: %s" % \
                (experimental_strategy, self.status)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
            return

        total_base_estimate = 0
        for f in files_in_metadata:
            seq_file = os.path.join(self.submission_directory, f['fileName'])

            try:
                total_base_estimate += base_estimate(seq_file, self.logger, self.checker)
            except Exception as ex:
                if str(ex) == "EOF marker is absent":
                    self.status = 'INVALID'
                    message = "Unable to continue with coverage estimation. EOF marker is absent, BAM file is probably " \
                        "truncated: %s. Validation result: %s" % \
                        (os.path.basename(seq_file), self.status)
                    self.message = message
                    self.logger.info(f'[{self.checker}] {message}')
                    return

                else:
                    raise Exception(str(ex))

        coverage = total_base_estimate / COVERAGE_THRESHOLD[experimental_strategy]['GENOME_SIZE']

        if coverage < COVERAGE_THRESHOLD[experimental_strategy]['MINIMUM']:
            self.status = 'INVALID'
            message = "Sequencing coverage estimate: %.2e, lower than mimimum threshold: %s for %s. " \
                "Validation result: %s" % \
                (coverage, str(COVERAGE_THRESHOLD[experimental_strategy]['MINIMUM']), experimental_strategy, self.status)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')

        elif coverage < COVERAGE_THRESHOLD[experimental_strategy]['WARNING']:
            self.status = 'WARNING'
            message = "Sequencing coverage estimate: %.2e. Lower than warning threshold: %s for %s. " \
                "Validation result: %s" % \
                (coverage, str(COVERAGE_THRESHOLD[experimental_strategy]['WARNING']), experimental_strategy, self.status)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')

        else:
            self.status = 'VALID'
            message = "Sequencing coverage estimate: %.2e. Validation status: %s" % (coverage, self.status)
            self.message = message
            self.logger.info(f'[{self.checker}] {message}')
