from app import db

class Tlorder(db.Model):
    __table__ = db.Model.metadata.tables['TMWIN.tlorder']

    def __repr__(self):
        return self.BILL_NUMBER
