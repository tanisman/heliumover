from util import app
from flask import jsonify
from flask_restful import Api
from model.proxy_group import proxy_group
from model.hotspot import hotspot
from model.rxpk import rxpk
from model.txpk import txpk
from controller.upstream import upstream
from controller.hotspots import hotspots
from controller.downstream import downstream
from api_config import API_HAS_DOWNSTREAM, API_HAS_UPSTREAM, API_HAS_HOTSPOT

@app.errorhandler(404)
def not_found(e):
    return jsonify({'message' : 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    if app.debug:
        return jsonify({'message' : str(e)}), 500
    return jsonify({'message' : 'Internal Server Error'}), 500

api = Api(app)
if API_HAS_HOTSPOT:
    api.add_resource(hotspots, "/hotspot/<string:address>")
if API_HAS_UPSTREAM:
    api.add_resource(upstream, "/upstream/<string:hotspot_address>")
if API_HAS_DOWNSTREAM:
    api.add_resource(downstream, "/downstream/<string:hotspot_address>")

if __name__ == '__main__':
    app.run( host = '0.0.0.0', port = 5000, debug = True, threaded = True )
