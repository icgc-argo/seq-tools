from abc import ABCMeta, abstractproperty, abstractmethod


class BaseChecker(object):
    __metaclass__ = ABCMeta

    def __init__(self, ctx, metadata):
        self._ctx = ctx
        self._metadata = metadata
        self._logger = ctx.obj['LOGGER']
        self._checks = ctx.obj['submission_report']['validation']['checks']
        self._checks.append({
            'checker': None,
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
