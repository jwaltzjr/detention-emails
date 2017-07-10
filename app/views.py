from collections import defaultdict
from flask import render_template, redirect, request, session, flash, url_for

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
            "Hello,\n\nThis is an automated message from KRC Logistics. We are currently at {location} in {city}, {st} for "
            "our scheduled appointment at {appointment} and our driver is being detained. Depending on when "
            "the driver is released, detention charges may apply on the following order.\n\nThank you and "
            "have a great day!\n\n{fb_info}"
        )
        confirmation_message = ''

        try:
            for fb in freight_bills:
                fb_info = ("FB# {fb}\nBOL#(s) {bols}\nPO#(s) {pos}\n").format(
                    fb=fb.bill_number,
                    bols=','.join(trace.trace_number for trace in fb.bol_numbers),
                    pos=','.join(trace.trace_number for trace in fb.po_numbers)
                )
                if stop_type == 'P':
                    email_message = email_message_base.format(
                        location=fb.origname,
                        city=fb.origcity,
                        st=fb.origprov,
                        appointment=fb.pick_up_by,
                        fb_info=fb_info
                    )
                elif stop_type == 'D':
                    email_message = email_message_base.format(
                        location=fb.destname,
                        city=fb.destcity,
                        st=fb.destprov,
                        appointment=fb.deliver_by,
                        fb_info=fb_info
                    )
                else:
                    email_message = 'An error occured.\n\n{}'.format(fb_info)
                email_ = KrcEmail(
                    ['jwaltzjr@krclogistics.com'],
                    subject='KRC Detention Notification for {}'.format(fb.bill_number),
                    message = email_message,
                    password = app.config['EMAIL_PASSWORD']
                )
                email_.send()
                flash('Email for {} was sent successfully'.format(fb.bill_number))
        except Exception as e:
            flash('Some or all of the emails were not sent.')
            flash(e)
            return redirect(url_for('index'))
        else:
            flash('All emails were sent successfully.')
            return redirect(url_for('index'))
    else:
        flash('An error occured. Please do not use the back or refresh buttons.')
        return redirect(url_for('index'))

