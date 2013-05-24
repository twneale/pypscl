from billy.core import db

from pscl.rollcall import RollcallBuilder


if __name__ == '__main__':

    spec = dict(state='ny', session='2013-2014', chamber='lower')
    chamber = spec['chamber']
    bill_ids = db.bills.find(spec).distinct('_id')

    builder = RollcallBuilder(spec=spec)
    votes = db.votes.find({'bill_id': {'$in': bill_ids}})
    for vote in votes:
        # Skip votes for the other chamber.
        if vote['chamber'] != chamber:
            continue
        builder.add_vote(vote)

    rc = builder.robject()
    import pdb; pdb.set_trace()
