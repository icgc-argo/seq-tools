from base_checker import BaseChecker


class Checker(BaseChecker):
    def __init__(self, ctx, metadata):
        super().__init__(ctx, metadata)
        self.checker = __name__.split('.')[-1]

    def check(self):
        if not self.metadata.get('read_groups'):
            message = "Missing 'read_groups' in the metadata JSON"
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
            return

        rg_ids = set()
        duplicated_ids = []
        for rg in self.metadata.get('read_groups'):
            if 'submitter_read_group_id' not in rg:
                message = "Required field 'submitter_read_group_id' not found in metadata JSON"
                self.logger.error(message)
                self.message = message
                self.status = 'INVALID'
                return

            if rg['submitter_read_group_id'] in rg_ids:
                duplicated_ids.append(rg['submitter_read_group_id'])
            else:
                rg_ids.add(rg['submitter_read_group_id'])

        if duplicated_ids:
            message =  "'submitter_read_group_id' duplicated in metadata: '%s'" % \
                ', '.join(duplicated_ids)
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "Read group ID uniqueness check status: VALID"
            self.message = message
            self.logger.info(message)
