import json
import pprint
import operator
from itertools import groupby

import numpy as np
from flask import Flask, render_template, make_response, request
from flask import redirect, flash

import settings
from core import mongo


app = Flask(__name__, static_folder='static')
app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY


@app.route("/")
def home():
    abbr = request.values.get('abbr')
    chamber = request.values.get('chamber')
    term = request.values.get('term')
    spec = dict(abbr=abbr, chamber=chamber, term=term)
    report = mongo.reports.find_one(spec)

    party = operator.itemgetter('party')
    party_verbose = dict(r='Republican', d='Democratic')
    points = []
    areas = []
    _points = list(sorted(report['points'], key=party))
    linedata = [point['x'] for point in _points]
    _, bins = np.histogram(linedata, bins=20)
    for partyletter, iterator in groupby(_points, key=party):
        key = party_verbose.get(partyletter, 'Other')
        values = list(iterator)
        for val in values:
            size = val['size']
            if size:
                size = size * 2000
                # size = (size + 5) * ((1 + size))
            else:
                size = 5
            val['size'] = size
        points.append(dict(key=key, values=values))

        linedata = [point['x'] for point in values]
        linedata = zip(*np.histogram(linedata, bins=bins))
        linedata = [dict(zip('yx', point)) for point in linedata]
        areas.append(dict(key=key, values=linedata))

    # Bubbles
    report['pp_points'] = pprint.pformat(points)
    report['points'] = json.dumps(points)

    # Areas
    report['pp_areas'] = pprint.pformat(areas)
    report['areas'] = json.dumps(areas)
    return render_template('home.html', report=report)


if __name__ == '__main__':
    app.run(debug=True)