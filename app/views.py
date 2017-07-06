from collections import defaultdict
from flask import render_template, redirect, request, session

from krc.krcemail import KrcEmail
from app import app
from . import models, forms

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

@app.route('/', methods=['GET','POST'])
def index():
    form = forms.TripNumberForm()
    if form.validate_on_submit():
        trip = models.Trip.query.filter_by(trip_number=form.trip_no.data).one()
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

        session['trip_stops'] = stops
                
        return render_template(
            'index.html',
            form=form,
            trip=trip,
            stops=stops.items()
        )
    return render_template(
        'index.html',
        form=form
    )

@app.route('/send-email', methods=['GET','POST'])
def send_email():
    stops = session.pop('trip_stops', None)
    stop_id = request.args.get('stop')
    if stops and stop_id:
        stop_type = stop_id[0]
        freight_bills = stops[stop_id]
        
        email_message_base = (
            "Hello,\n\nThis is an automated message from KRC Logistics. We are currently at {location} for "
            "our scheduled appointment at {appointment} and our driver is being detained. Depending on when "
            "the driver is released, detention charges may apply on the following order.\n\nThank you and "
            "have a great day!\n\n{fb_info}"
        )
        test_message = ''
        
        for fb in freight_bills:
            bol_list = ','.join(fb.trace_numbers.filter_by(trace_type='B').all())
            po_list = ','.join(fb.trace_numbers.filter_by(trace_type='P').all())
            fb_info = ("FB# {fb}\nBOL#(s) {bols}\nPO#(s) {pos}\n").format(
                fb=fb.bill_number,
                bols=bol_list,
                pos=po_list
            )
            if stop_type == 'P':
                email_message = email_message_base.format(
                    location=fb.origname,
                    appointment=fb.pick_up_by,
                    fb_info=fb_info
                )
            elif stop_type == 'D':
                email_message = email_message_base.format(
                    location=fb.destname,
                    appointment=fb.deliver_by,
                    fb_info=fb_info
                )
            else:
                email_message = 'An error occured.\n\n{}'.format(fb_info)
            test_message += (email_message + '\n\n')
        return test_message
    else:
        return 'An error occured.'

