from datetime import datetime
from util import db

class rxpk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('proxy_group.id'), nullable=False)
    poc_id = db.Column(db.String(128), unique=True, nullable=False)
    payload = db.Column(db.String(540), nullable=False)
    receiver_lat = db.Column(db.Float(precision=53), nullable=False)
    receiver_lng = db.Column(db.Float(precision=53), nullable=False)
    receiver_address = db.Column(db.String(128), nullable=False)
    receiver_gain = db.Column(db.Integer, nullable=False)
    received_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    group = db.relationship('proxy_group', backref=db.backref('rxpk', lazy='dynamic'))

    def __repr__(self):
        return f"<rxpk {self.poc_id}>"