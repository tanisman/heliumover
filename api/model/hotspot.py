from datetime import datetime
from util import db

class hotspot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('proxy_group.id'), nullable=False)
    address = db.Column(db.String(128), unique=True, nullable=False)
    lat = db.Column(db.Float(precision=53), nullable=False)
    lng = db.Column(db.Float(precision=53), nullable=False)
    gain = db.Column(db.Integer, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_pocs_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<hotspot %r>' % self.address