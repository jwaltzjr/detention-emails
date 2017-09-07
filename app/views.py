from collections import OrderedDict
from flask import render_template, redirect, request, session, flash, url_for
from sqlalchemy.orm.exc import NoResultFound

from krc.krcemail import KrcEmail
from app import app, db
from . import models, forms

@app.route('/', methods=['GET','POST'])
def index():
    form = forms.TripNumberForm()
    if form.validate_on_submit():
        try:
            trip = models.Trip.query.filter_by(trip_number=form.trip_no.data).one()
        except NoResultFound:
            flash('Trip {} was not found.'.format(form.trip_no.data))
            return redirect(url_for('index'))

        terminal_plans = trip.termplans.filter_by(
            trip_number=trip.trip_number
        )
        
        stops = OrderedDict()
        for fb in terminal_plans:
            if fb.tx_type == 'P':
                group = 'PICKUP at {} scheduled for {}'.format(fb.tlorder.origin, fb.tlorder.pick_up_by)
                stops.setdefault(group, []).append(fb.tlorder)
            elif fb.tx_type == 'D':
                group = 'DELIVERY to {} scheduled for {}'.format(fb.tlorder.destination, fb.tlorder.deliver_by)
                stops.setdefault(group, []).append(fb.tlorder)

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

@app.route('/send-detention', methods=['GET','POST'])
def send_detention():
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

        current_timestamp = db.func.now()
                
        try:
            for fb in freight_bills:
                if fb.bill_to_emails:
                    fb_info = ("FB# {fb}\nBOL#(s) {bols}\nPO#(s) {pos}\n").format(
                        fb=fb.bill_number,
                        bols=','.join(trace.trace_number for trace in fb.bol_numbers),
                        pos=','.join(trace.trace_number for trace in fb.po_numbers)
                    )
                    tlorder_fb = models.Tlorder.query.filter_by(detail_line_id=fb.detail_line_id).one()

                    emails = [app.config['DISPATCH_EMAIL'], fb.csr_email]
                    for e in fb.bill_to_emails:
                        emails.append(e)
                    
                    if stop_type == 'P':
                        email_message = email_message_base.format(
                            location=fb.origname,
                            city=fb.origcity,
                            st=fb.origprov,
                            appointment=fb.pick_up_by,
                            fb_info=fb_info
                        )
                        if tlorder_fb.pu_notify:
                            tlorder_fb.pu_notify.DATE = current_timestamp
                            db.session.commit()
                        else:
                            new_cdf = models.CustDef(41, fb.detail_line_id, date_=current_timestamp)
                            db.session.add(new_cdf)
                            db.session.commit()
                    elif stop_type == 'D':
                        email_message = email_message_base.format(
                            location=fb.destname,
                            city=fb.destcity,
                            st=fb.destprov,
                            appointment=fb.deliver_by,
                            fb_info=fb_info
                        )
                        if tlorder_fb.del_notify:
                            tlorder_fb.del_notify.DATE = current_timestamp
                            db.session.commit()
                        else:
                            new_cdf = models.CustDef(42, fb.detail_line_id, date_=current_timestamp)
                            db.session.add(new_cdf)
                            db.session.commit()
                    else:
                        email_message = 'An error occured.\n\n{}'.format(fb_info)
                    email_ = KrcEmail(
                        emails,
                        subject='KRC Detention Notification for {}'.format(fb.bill_number),
                        message = email_message,
                        password = app.config['EMAIL_PASSWORD']
                    )
                    email_.send()
                    flash('Email for {} was sent successfully.'.format(fb.bill_number))
                else:
                    flash('Email for {} was not sent - no detention email for {}.'.format(
                        fb.bill_number, fb.billto.name
                    ))
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


@app.route('/send-late', methods=['GET','POST'])
def send_late():
    stops = session['trip_stops']
    stop_id = request.args.get('stop')
    if stops and stop_id:
        stop_type = stop_id[0]
        freight_bills = stops[stop_id]

        FB_CHOICES = []
        for fb in freight_bills:
            FB_CHOICES.append((fb.bill_number, '{} - {}'.format(fb.bill_number, fb.callname)))

        form = forms.UndeliveredForm()
        form.freight_bills.choices = FB_CHOICES

        if form.validate_on_submit():
            email_message_base = (
                "Hello,\n\nThis message is being sent to notify you that {fb_no} will not be delivering "
                "today. Please see routing for reschedule information.\n\nFB# {fb_no}\nCONSIGNEE: "
                "{consignee}\nAPPT END: {appt}\nREASON: {reason}\nNOTES: {notes}\n\nThank you and have a "
                "great day!\n\n-KRC Dispatch"
            )
            
            for fb in freight_bills:
                if fb.bill_number in (form.freight_bills.data):
                    emails = ['jwaltzjr@krclogistics.com']
                    #emails = [app.config['DISPATCH_EMAIL'], fb.csr_email]
                    #for e in app.config['ROUTING_EMAILS']:
                    #    emails.append(e)

                    try:
                        email_message = email_message_base.format(
                            fb_no = fb.bill_number.strip(),
                            consignee = fb.destination,
                            appt = fb.deliver_by_end,
                            reason = dict(forms.UNDELIVERED_CHOICES).get(form.reason.data),
                            notes = form.notes.data
                        )
                        email_ = KrcEmail(
                            emails,
                            subject='KRC Undelivered Notification for {}'.format(fb.bill_number),
                            message = email_message,
                            password = app.config['EMAIL_PASSWORD']
                        )
                        email_.send()
                        flash('Email for {} was sent successfully.'.format(fb.bill_number))
                    except Exception as e:
                        flash('ERROR: Email for {} was not sent!.'.format(fb.bill_number))
                        flash(e)
            stops = session.pop('trip_stops', None)
            return redirect(url_for('index'))
        else:
            return render_template(
                'confirm_undelivered.html',
                form=form
            )

