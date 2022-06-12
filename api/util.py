from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api_config import DB_URI

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    return app

app = create_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)