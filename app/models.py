from app import db

class Tlorder(db.Model):
    __table__ = db.Model.metadata.tables['TMWIN.tlorder']
    termplans = db.relationship('TermPlan', backref = 'tlorder')

    def __repr__(self):
        return self.bill_number

class TermPlan(db.Model):
    __table__ = db.Model.metadata.tables['TMWIN.tlorder_term_plan']

    def __repr__(self):
        return '<{} {} - {}>'.format(self.trip_number, self.tx_type, self.detail_line_id)

class Trip(db.Model):
    __table__ = db.Model.metadata.tables['TMWIN.trip']
    termplans = db.relationship('TermPlan', backref = 'trip')

    def __repr__(self):
        return self.trip_number
