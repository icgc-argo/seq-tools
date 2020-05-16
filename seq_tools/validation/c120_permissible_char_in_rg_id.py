import re
from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata)
        self.checker = __name__.split('.')[-1]

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' section in the metadata JSON"
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
            return

        offending_ids = set()
        for rg in self.metadata.get('read_groups'):
            if 'submitter_read_group_id' not in rg:
                message = "Required field 'submitter_read_group_id' not found in metadata JSON"
                self.logger.error(message)
                self.message = message
                self.status = 'INVALID'
                return

            if not re.match(r'^[a-zA-Z0-9_\.\-]{2,}$', rg['submitter_read_group_id']):
                offending_ids.add(rg['submitter_read_group_id'])

        if offending_ids:
            message =  "'submitter_read_group_id' in metadata contains invalid character or " \
                "is shorter then 2 characters: '%s'. " \
                "Permissible characters include: a-z, A-Z, 0-9, - (hyphen), " \
                "_ (underscore) and . (dot)" % ', '.join(offending_ids)
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "Read group ID permissible character check status: VALID"
            self.message = message
            self.logger.info(message)
