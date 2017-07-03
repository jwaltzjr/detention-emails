from app import db

class TermPlan(db.Model):
    __tablename__ = 'TMWIN.tlorder_term_plan'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine, 'extend_existing': True}
    detail_line_id = db.Column(db.Integer, db.ForeignKey('TMWIN.tlorder.detail_line_id'))
    trip_number = db.Column(db.Integer, db.ForeignKey('TMWIN.trip.trip_number'))

    def __repr__(self):
        return '<{} {} - {}>'.format(self.trip_number, self.tx_type, self.detail_line_id)

class Tlorder(db.Model):
    __tablename__ = 'TMWIN.tlorder'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine, 'extend_existing': True}
    termplans = db.relationship(TermPlan, backref = 'tlorder', lazy='dynamic')

    def __repr__(self):
        return self.bill_number

class Trip(db.Model):
    __tablename__ = 'TMWIN.trip'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine, 'extend_existing': True}
    termplans = db.relationship(TermPlan, backref = 'trip', lazy='dynamic')

    def __repr__(self):
        return self.trip_number
