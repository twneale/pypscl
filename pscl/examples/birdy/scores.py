import sys
import json
import logging
from itertools import product
from collections import Counter, defaultdict

import networkx
import numpy as np
from pandas import DataFrame
from sunlight import openstates
from pscl import Rollcall

from core import mongo, IterBills


class DataQualityError(Exception):
    '''Raised if calculation is aborted due to data quality issues.
    '''

class ScoreCalculator(object):
    '''Given a state, chamber, and term or session, calculate
    the cosponsorship pagerank, effectiveness, and ideal point
    scores for each legislator.
    '''
    def __init__(self, abbr, chamber, term=None, session=None):
        self.abbr = abbr
        self.session = session
        self.term = term
        self.chamber = chamber
        self.bills = IterBills(
            abbr, chamber, session=session, term=term)

    def get_pagerank(self):
        '''Create a co-sponsorship digraph based on the information from
        the Open States API and calculate the pagerank of each legislator.
        '''
        G = networkx.DiGraph()
        number_of_bills = 0

        for bill in self.bills:
            sponsors = bill['sponsors']
            if len(sponsors) < 2:
                continue

            # Separate sponsors into primary, secondary.
            primary = []
            secondary = []
            for sponsor in sponsors:
                if sponsor['leg_id'] is None:
                    continue
                if sponsor['type'] == 'primary':
                    primary.append(sponsor['leg_id'])
                else:
                    secondary.append(sponsor['leg_id'])

            # Add them to the network.
            if primary and secondary:
                for primary, secondary in product(primary, secondary):
                    try:
                        G[secondary][primary]['weight'] += 1
                    except KeyError:
                        G.add_edge(secondary, primary, weight=1)

        if not G.nodes():
            # Known offenders: CO
            data = dict(abbr=self.abbr, chamber=self.chamber)
            msg = ("Can't generate PageRank scores due to lack of secondary "
                   "sponsorship data: %r.")
            raise DataQualityError(msg % (data,))

        return networkx.pagerank_numpy(G)

    def get_effectiveness(self):
        '''Create an effectiveness score for each legislator relative to
        all the others based on the extent to which bills by each leg'r
        are passed on the chamber of origin, the other chamber, or into law.
        '''
        legislators = Counter()
        number_of_bills = 0
        chamber = self.chamber

        # Calculate the scores.
        for bill in self.bills:
            sponsors = bill['sponsors']

            # Separate sponsors into primary, secondary.
            primary = []
            secondary = []
            for sponsor in sponsors:
                if sponsor['type'] == 'primary':
                    primary.append(sponsor['leg_id'])
                else:
                    secondary.append(sponsor['leg_id'])

            for sponsor in primary:
                if chamber == 'upper':
                    other_chamber = 'lower'
                else:
                    other_chamber = 'upper'
                if bill['action_dates']['passed_%s' % self.chamber]:
                    legislators[sponsor] += 1
                if bill['action_dates']['passed_%s' % other_chamber]:
                    legislators[sponsor] += 5
                if bill['action_dates']['signed']:
                    legislators[sponsor] += 10

        # Normalize the scores.
        vals = np.array(map(float, legislators.values()))
        normed = (vals / sum(vals) * 250)
        normed = dict(zip(vals, normed))
        newvals = {}
        for leg_id, value in legislators.items():
            newvals[leg_id] = normed.get(value)
        return newvals

    def get_idealpoints(self):

        YES = 1
        NO = 2
        OTHER = 3

        votedata = defaultdict(dict)
        vote_vals = dict(yes_votes=YES, no_votes=NO, other_votes=OTHER)
        leg_ids = set()

        vote_keys = 'yes_votes, no_votes, other_votes'.split(', ')
        for vote in self.bills.itervotes():
            for k in vote_keys:
                for voter in vote[k]:
                    leg_id = voter['leg_id']
                    if leg_id is None:
                        continue
                    leg_ids.add(leg_id)
                    votedata[vote['id']][leg_id] = vote_vals[k]
        leg_ids = list(filter(None, leg_ids))

        # for vote_id, votes in votedata.items():
        #     votedata[vote_id] = map(lambda leg_id: votes.get(leg_id, MISSING), leg_ids)

        # Convert the dict into a pandas DataFrame.
        dataframe = DataFrame(votedata, index=leg_ids)
        dataframe.fillna(value=9)

        # Create a rollcall object similar to pscl's.
        rollcall = Rollcall.from_dataframe(dataframe,
            yea=[YES],
            nay=[NO],
            missing=[OTHER],
            not_in_legis=0.0,
            legis_names=leg_ids)

        return rollcall.ideal().xbar


def get_scores(abbr, chamber, **kwargs):
    '''Helper function for ScoreCalculator monster.
    '''
    scores = ScoreCalculator(abbr, chamber, **kwargs)

    logging.info('Starting ideal point calculation...')
    idealpoints = scores.get_idealpoints()
    logging.info('...done')

    logging.info('Starting effectiveness calculation...')
    effectiveness = scores.get_effectiveness()
    logging.info('...done')

    logging.info('Starting pagerank calculation...')
    pageranks = scores.get_pagerank()
    logging.info('...done')

    return dict(
        effectiveness=effectiveness,
        pageranks=pageranks,
        idealpoints=idealpoints)


def party_letter(party):
    parties = 'rd'
    letter = party.lower()[0]
    if letter in parties:
        return letter
    else:
        return 'o'


def import_scores(abbr, chamber, term):
    '''Write the scores into mongo.
    '''
    scores = get_scores(abbr, chamber, term=term)

    # Get a set of all ids.
    ids = set(scores['idealpoints'].keys())
    ids = filter(None, ids)

    points = []
    for id in ids:

        # Save the legislator.
        logging.debug('Fetching legislator %r' % id)
        legislator = openstates.legislator_detail(id)
        legislator['_id'] = legislator['id']
        mongo.legislators.save(legislator)

        party = party_letter(legislator.get('party', 'o'))
        logging.debug('Party is %r' % party)

        # Calculate the point data.
        point = dict(
            x=scores['idealpoints'][id],
            # If no effectiveness score, s/he got no bills passed.
            y=scores['effectiveness'].get(id, 0),
            # If no PR score, s/he had no consponsorships.
            size=scores['pageranks'].get(id, 0),
            party=party,
            )
        points.append(point)

    report = dict(
        term=term,
        abbr=abbr,
        chamber=chamber,
        points=points)
    mongo.reports.save(report)


if __name__ == '__main__':
    import_scores(*sys.argv[1:])
    # import_scores('ny', 'lower', term='2011-2012')
