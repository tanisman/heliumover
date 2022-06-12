from flask import request
from flask_restful import Resource
from util import db
from model.hotspot import hotspot

class hotspots(Resource):
    def post(self, address):
        requesterq = hotspot.query.filter_by(address=address)
        if requesterq.count() == 0:
            return {'message' : 'hotspot is not registered'}, 403

        requester = requesterq.first()

        content = request.get_json()
        lat = content["lat"]
        lng = content["lng"]
        gain = content["gain"]

        requester.lat = lat
        requester.lng = lng
        requester.gain = gain

        db.session.commit()
        return {'message' : 'hotspot updated'}, 200


