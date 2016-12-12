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
        userId = request.json.get('UserId', '')
        phone  = request.json.get('Phone', '')
        token  = request.json.get('Token', '')
        user   = None
        if phone:
            user = models.User.query.filter_by(phone=phone).first()
            if not user:
                user = models.User.query.get(userId)
        else:
            user = models.User.query.get(userId)
        if not user:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '不存在该用户!'}), 400
        if token != user.token:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '输入的token错误!'}), 400
        return func(*args, **kwargs)
    return wrapped


def verify_request_token1(func):
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

def verify_user_exist(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        userId = request.json.get("UserId", '')
        phone  = request.json.get('Phone', '')
        user   = models.User.getUserByIdOrPhoneOrMail(id=userId, phone=phone)

        if not user:
            if phone:
                return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "User phone={} does't exist".format(phone)}), 400
            if userId:
                return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "User id={} does't exist".format(userId)}), 400
        else:
            return func(*args, **kwargs)
    return wrapped
