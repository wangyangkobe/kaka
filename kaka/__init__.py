# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@localhost/kaka_db?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret string'
db = SQLAlchemy(app)
logger = app.logger

# toList接口每个用户返回用户状态开关,true：打开 false：关闭
os.environ['needDetails'] = 'true'

# http的域名
HOST = 'http://sdk.open.api.igexin.com/apiex.htm'

APPKEY = "Ljo9P2kC5A93MhCh6BhnC7"
APPID = "DTTWD485HI6NNpfL0afH25"
MASTERSECRET = "sEat0K6eGkAMdatKEfnzi6"
CID = ""
Alias = '请输入别名'
DEVICETOKEN = ""


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
