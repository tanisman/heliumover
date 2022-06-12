from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from util import db

class proxy_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return '<proxy_group %r>' % self.name