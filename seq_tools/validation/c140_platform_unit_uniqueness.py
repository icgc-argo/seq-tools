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

        pus = set()
        duplicated_pus = []
        for rg in self.metadata.get('read_groups'):
            if 'platform_unit' not in rg:
                message = "Required field 'platform_unit' not found in metadata JSON"
                self.logger.error(message)
                self.message = message
                self.status = 'INVALID'
                return

            if rg['platform_unit'] in pus:
                duplicated_pus.append(rg['platform_unit'])
            else:
                pus.add(rg['platform_unit'])

        if duplicated_pus:
            message =  "'platform_unit' duplicated in metadata: '%s'" % \
                ', '.join(duplicated_pus)
            self.logger.error(message)
            self.message = message
            self.status = 'INVALID'
        else:
            self.status = 'VALID'
            message = "Platform unit uniqueness check status: VALID"
            self.message = message
            self.logger.info(message)
