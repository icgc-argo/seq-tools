from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata)
        self.checker = __name__.split('.')[-1]

    def check(self):
        if not self.metadata.get('samples'):
            message = "Missing 'samples' section in the metadata JSON"
            self.message = message
            self.status = 'INVALID'
            self.logger.error(message)
            return

        if len(self.metadata.get('samples')) != 1:
            message =  "'samples' section must contain exactly one sample in metadata, %s found" % \
                len(metadata.get('samples'))
            self.message = message
            self.status = 'INVALID'
            self.logger.error(message)
        else:
            message = "One and only one sample check status: VALID"
            self.status = 'VALID'
            self.message = message
            self.logger.info(message)
