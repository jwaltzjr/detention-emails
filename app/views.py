from app import app
from . import models

@app.route('/')
def index():
    fb = models.Tlorder.query.first()
    return fb.bill_number
