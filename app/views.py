from collections import defaultdict
from flask import render_template

from app import app
from . import models

@app.route('/test')
def test():
    trip = models.Trip.query.filter_by(trip_number=10321).one()
    freight_bills = trip.termplans.filter_by(
        trip_number=trip.trip_number
    )
    
    stops = defaultdict(list)
    for fb in freight_bills:
        if fb.tx_type == 'P':
            group = 'P-{}-{}'.format(fb.tlorder.origin, fb.tlorder.pick_up_by)
            stops[group].append(fb.tlorder)
        elif fb.tx_type == 'D':
            group = 'D-{}-{}'.format(fb.tlorder.destination, fb.tlorder.deliver_by)
            stops[group].append(fb.tlorder)
            
    return render_template(
        'testing.html',
        trip = trip,
        freight_bills = freight_bills,
        stops = stops.items()
    )
