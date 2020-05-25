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


from abc import ABCMeta, abstractmethod


class BaseChecker(object):
    __metaclass__ = ABCMeta

    def __init__(self, ctx, metadata, checker_name):
        self._ctx = ctx
        self._metadata = metadata
        self._logger = ctx.obj['LOGGER']
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
    def metadata(self):
        return self._metadata

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
