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
import functools
from abc import ABCMeta, abstractmethod


class BaseChecker(object):
    __metaclass__ = ABCMeta

    def __init__(self, ctx, metadata, checker_name):
        self._ctx = ctx
        self._metadata = metadata
        self._logger = ctx.obj['LOGGER']
        self._submission_directory = ctx.obj['submission_report'].get('submission_directory')
        self._files = ctx.obj['submission_report'].get('files')
        self._checks = ctx.obj['submission_report']['validation']['checks']
        self._checks.append({
            'checker': checker_name,
            'status': None,
            'message': None
        })

    @property
    def ctx(self):
        return self._ctx

    @property
    def submission_directory(self):
        return self._submission_directory

    @property
    def metadata(self):
        return self._metadata

    @property
    def files(self):
        return self._files

    @property
    def logger(self):
        return self._logger

    @property
    def checker(self):
        return self._checks[-1]['checker']

    @checker.setter
    def checker(self, value):
        self._checks[-1]['checker'] = value

    @property
    def message(self):
        return self._checks[-1]['message']

    @message.setter
    def message(self, value):
        self._checks[-1]['message'] = value

    @property
    def status(self):
        return self._checks[-1]['status']

    @status.setter
    def status(self, value):
        self._checks[-1]['status'] = value

    @abstractmethod
    def check(self):
        pass

    def _catch_exception(f):
        @functools.wraps(f)
        def func(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as ex:
                _self = args[0]
                _self.status = 'UNKNOWN'
                message = "An exception occurred during the execution of this checker. " \
                    "This is likely due to problem(s) identified by earlier check(s), " \
                    "please fix reported problem and then run the validation again."
                _self.message = "%s More information of the exception can be found " \
                    "in the latest log file under: %s" \
                    % (message, os.path.join(
                        os.path.basename(_self.submission_directory), 'logs', ''))
                _self.logger.info("[%s] %s Additional message: %s" % (
                    _self.checker, message, str(ex)))
        return func

    _catch_exception = staticmethod(_catch_exception)
