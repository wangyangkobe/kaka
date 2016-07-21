# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@localhost/kaka_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret string'
db = SQLAlchemy(app)
logger = app.logger

from kaka.api.views import api_blueprint
from kaka.admin.views import admin_blueprint
from kaka.user.views import user_blueprint

# Return validation errors as JSON
@app.errorhandler(422)
def handle_request_parsing_error(err):
    _code, msg = getattr(err, 'status_code', 400), getattr(err.data['exc'], 'messages', 'Invalid Request')
    return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': "{}: {}".format(msg.keys()[0], msg.values()[0])}), 400


app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(user_blueprint, url_prefix='/user')