from util import app, db
from flask import jsonify
from flask_restful import Api
from flask_admin import Admin
from model.proxy_group import proxy_group
from model.hotspot import hotspot
from model.rxpk import rxpk
from model.txpk import txpk
from model.admin_user import admin_user
from controller.upstream import upstream
from controller.hotspots import hotspots
from controller.downstream import downstream
from admin.admin_view import admin_view
from admin.index_view import index_view, init_login
from api_config import API_HAS_DOWNSTREAM, API_HAS_UPSTREAM, API_HAS_HOTSPOT, API_HAS_ADMIN

app.config['SECRET_KEY'] = '!R8^d[nPya~+eHpB'

@app.errorhandler(404)
def not_found(e):
    return jsonify({'message' : 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    if app.debug:
        return jsonify({'message' : str(e)}), 500
    return jsonify({'message' : 'Internal Server Error'}), 500

if API_HAS_ADMIN:
    app.config['FLASK_ADMIN_SWATCH'] = 'pulse'
    init_login()
    admin = Admin(app, name='heliumover', index_view=index_view(), base_template='my_master.html', template_mode='bootstrap4')
    admin.add_view(admin_view(admin_user, db.session))
    admin.add_view(admin_view(proxy_group, db.session))
    admin.add_view(admin_view(hotspot, db.session))
    admin.add_view(admin_view(rxpk, db.session))
    admin.add_view(admin_view(txpk, db.session))

api = Api(app)
if API_HAS_HOTSPOT:
    api.add_resource(hotspots, "/hotspot/<string:hotspot_address>")
if API_HAS_UPSTREAM:
    api.add_resource(upstream, "/upstream/<string:hotspot_address>")
if API_HAS_DOWNSTREAM:
    api.add_resource(downstream, "/downstream/<string:hotspot_address>")

if __name__ == '__main__':
    app.run( host = '0.0.0.0', port = 5000, debug = True, threaded = True )
