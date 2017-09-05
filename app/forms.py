from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, SelectMultipleField, SelectField,
    TextAreaField, widgets
)
from wtforms.validators import DataRequired

UNDELIVERED_CHOICES = [
    ('hos', 'HOS'),
    ('prev', 'Held at Prev. Stop'),
    ('mbd', 'Mechanical Breakdown'),
    ('r-hos', 'REFUSED - HOS'),
    ('r-appt', 'REFUSED - No Appointment'),
    ('r-temp', 'REFUSED - Temperature'),
    ('r-other', 'REFUSED - Other'),
    ('other', 'Other')
]

class TripNumberForm(FlaskForm):
    trip_no = IntegerField(
        'trip_no',
        validators=[DataRequired()]
    )

class UndeliveredForm(FlaskForm):
    freight_bills = SelectMultipleField(
        'freight_bills',
        choices=[],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
    reason = SelectField(
        'reason',
        choices=UNDELIVERED_CHOICES
    )
    notes = TextAreaField(
        'notes'
    )
