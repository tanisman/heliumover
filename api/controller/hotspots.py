from flask import request
from flask_restful import Resource
from util import db
from model.hotspot import hotspot
from auth import authorize_hotspot

class hotspots(Resource):
    @authorize_hotspot
    def post(self, hotspot_address):
        requester = hotspot.query.filter_by(address=hotspot_address).first()
        
        content = request.get_json()
        lat = content["lat"]
        lng = content["lng"]
        gain = content["gain"]

        requester.lat = lat
        requester.lng = lng
        requester.gain = gain

        db.session.commit()
        return {'message' : 'hotspot updated'}, 200


