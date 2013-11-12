import sys
import json
import collections

from billy.core import db


def party(partystring):
    if partystring.lower().startswith('r'):
        return 'r'
    elif partystring.lower().startswith('d'):
        return 'd'
    else:
        return 'g'


def main(abbr, session, chamber):
    ids = set()
    data = collections.defaultdict(dict)
    for fn in 'xbar eff pg'.split():
        vals = ('.'.join([abbr, session, chamber]), fn)
        with open('experimental/birdy/data/%s-%s.json' % vals) as f:
            for _id, rank in json.load(f).items():
                ids.add(_id)
                data[_id][fn] = rank

    legdict = {}
    for leg in db.legislators.find({'_id': {'$in': tuple(ids)}}):
        legdict[leg['_id']] = leg

    for _id, details in data.items():
        if _id == 'null':
            continue
        record = legdict[_id]
        details['party'] = party(record['party'])
        details['full_name'] = record['full_name']

    values = data.values()
    for thingy in values:
        if 'xbar' not in thingy:
            values.remove(thingy)

    with open('experimental/birdy/data/%s-data.json' % '.'.join([abbr, session, chamber]), 'w') as f:
        json.dump(values, f)


if __name__ == '__main__':
    main(*sys.argv[1:])