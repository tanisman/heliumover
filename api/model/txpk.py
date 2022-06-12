from datetime import datetime
from util import db

class txpk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('proxy_group.id'), nullable=False)
    poc_id = db.Column(db.String(128), unique=True, nullable=False)
    payload = db.Column(db.String(540), nullable=False)
    transmitter_lat = db.Column(db.Float(precision=53), nullable=False)
    transmitter_lng = db.Column(db.Float(precision=53), nullable=False)
    transmitter_address = db.Column(db.String(128), nullable=False)
    transmitted_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<rxpk %r>' % self.poc_id