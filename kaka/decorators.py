# -*- coding: utf-8 -*-
from flask import request, jsonify
from kaka import models
from functools import wraps

def verify_request_json(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if request.json:
            return func(*args, **kwargs)
        else:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '请求的payload数据不是json'}), 400
    return wrapped

def verify_request_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        userName = request.json.get('User', '')
        token    = request.json.get('Token', '')
        if userName and token and models.User.checkUserToken(userName, token):
            return func(*args, **kwargs)
        elif not userName:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '请求的paylod中无userName'}), 400
        elif not token:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '请求的paylod中无Token'}), 400
        else:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': 'token错误!'}), 400 
    return wrapped