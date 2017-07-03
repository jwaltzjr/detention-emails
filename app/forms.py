from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired

class TripNumberForm(FlaskForm):
    trip_no = IntegerField(
        'trip_no',
        validators=[DataRequired()]
    )
