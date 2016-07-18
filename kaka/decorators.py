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
        userId   = request.json.get('UserId', '')
        token    = request.json.get('Token', '')
        if userId and token and models.User.checkUserToken(userId, token):
            return func(*args, **kwargs)
        elif not userId:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '请求的paylod中无userId'}), 400
        elif not token:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '请求的paylod中无Token'}), 400
        else:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': 'token错误!'}), 400 
    return wrapped