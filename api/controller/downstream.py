from flask import request
from flask_restful import Resource
from util import db
from model.hotspot import hotspot
from model.txpk import txpk
from auth import authorize_hotspot
from helium.radio import decrypt_radio
import json

class downstream(Resource):
    @authorize_hotspot
    def post(self, hotspot_address):
        pull_data_msg = request.get_json()
        msg = decrypt_radio(pull_data_msg["data"])
        transmitter = hotspot.query.filter_by(address=hotspot_address).first()

        new_txpk = txpk(
            group_id=transmitter.group_id,
            poc_id=msg.poc_id,
            payload=json.dumps(pull_data_msg),
            transmitter_lat=transmitter.lat,
            transmitter_lng=transmitter.lng,
            transmitter_address=hotspot_address,
        )
        db.session.add(new_txpk)
        db.session.commit()
        return {'message' : 'PoC succesfuly pushed'}, 200
