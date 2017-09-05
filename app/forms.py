from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired

class TripNumberForm(FlaskForm):
    trip_no = IntegerField(
        'trip_no',
        validators=[DataRequired()]
    )

class UndeliveredForm(FlaskForm):
    freight_bills = SelectMultipleField(
        'Which freight bills are undelivered?',
        choices=[],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
