import logging

import pymongo
from sunlight import openstates

import settings


conn = pymongo.MongoClient(host=settings.MONGO_HOST)
mongo = getattr(conn, settings.MONGO_DATABASE_NAME)
mongo.authenticate(settings.MONGO_USER, settings.MONGO_PASSWORD)


logging.basicConfig(level=logging.DEBUG)


class CachedAttr(object):
    '''Computes attr value and caches it in the instance.'''

    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


class TooFewBillsError(Exception):
    '''Raised when the search window doesn't contain enough
    bills for a meaningful calculation, where enough is
    arbitrarily defined as 1000.
    '''


class IterBills(object):

    PER_PAGE = 500

    @CachedAttr
    def data(self):
        return {}

    @CachedAttr
    def bill_metadata(self):
        spec = {
            'state': self.abbr,
            'chamber': self.chamber,
            'per_page': self.PER_PAGE}
        if self.term and not self.session:
            if isinstance(self.term, basestring):
                # Search the specified term.
                spec['search_window'] = 'term:' + self.term
            else:
                # Search the current term.
                spec['search_window'] = 'term'
        elif self.session:
            if isinstance(self.session, basestring):
                # Search the specified session.
                spec['search_window'] = 'session:' + self.session
            else:
                # Search the current session.
                spec['search_window'] = 'session'

        logging.info('Fetching bill metadata...')
        page = 1
        meta = []
        while True:
            spec.update(page=page)
            logging.debug('Fetching metadata: %r' % spec)
            meta += openstates.bills(**spec)
            if not meta:
                break
            if self.limit < (page * self.PER_PAGE):
                break
            page += 1
        logging.info('...done.')

        if self.limit:
            meta = meta[:self.limit]

        if len(meta) < 100:
            # If the term or session contains too few bills for a
            # meaningful calculation, complain/bail.
            msg = 'Too few bills found (%d); aborting. %r'
            data = dict(
                abbr=self.abbr,
                session=self.session,
                term=self.term)
            raise TooFewBillsError(msg % (len(meta), data,))

        return meta

    def __init__(self, abbr, chamber, session=None, term=None, limit=None):
        if not any([term, session]):
            raise ValueError('Supply either a term or session.')
        self.abbr = abbr
        self.session = session
        self.term = term
        self.chamber = chamber
        self.limit = limit
        self.per_page = min(limit or self.PER_PAGE, self.PER_PAGE)

    def __iter__(self):
        self.index = 0
        data = self.data
        while True:
            try:
                yield next(self)
                self.index += 1
            except IndexError:
                return

    def next(self):
        data = self.data
        bill = self.bill_metadata[self.index]
        bill_id = bill['id']
        if bill_id in data:
            return data[bill_id]
        else:
            logging.debug('Fetching bill: %r' % bill_id)
            bill = openstates.bill(bill_id)
            data[bill_id] = bill
            return bill

    def itervotes(self):
        for bill in self:
            for vote in bill['votes']:
                yield vote