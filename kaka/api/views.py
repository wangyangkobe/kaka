# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/register', methods=['POST'])
@verify_request_json
def register():    
    userName = request.json.get('User', '')
    passWord = request.json.get('Password', '')
    phone    = request.json.get('Phone', '')
    email    = request.json.get('Email', '')
    code     = request.json.get('Code', '')
    pushToken= request.json.get('PushToken', '')
    userType = request.json.get('UserType', 0)
    registerType = request.json.get('RegisterType', 0)
    user = models.User(userName, passWord, phone, email, code, pushToken, userType=userType, registerType=registerType)
    try:
        user.verifyUser()
        db.session.add(user)
        db.session.commit()
        return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '注册成功!'}), 200
    except ValueError, error:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': error.message}), 400
    except Exception, error:
        return jsonify({'Status': 'Failed', 'StatusCode': -2, 'Msg': error.message}), 400
    
@api_blueprint.route('/login', methods=['POST'])
@verify_request_json
def login():
    userName = request.json.get('User', '')
    passWord = request.json.get('Password', '')
    
    user = models.User.getUserByUserName(userName)
    if user:
        if user.checkPassWord(passWord):
            user.token = user.get_auth_token()
            user.pushToken = request.json.get('PushToken', '')
            db.session.merge(user)
            db.session.commit()
            session['api_session_token'] = user.token
            return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '登录成功!', 'Token': user.token}), 200
        else:
            return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '密码错误'}), 400 
    else:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '输入的用户名不存在'}), 400
    
@api_blueprint.route('/delMachines',  methods=['POST'])
@verify_request_json
@verify_request_token
def delMachines():
    userName = request.json.get('User', '')
    return jsonify(userName)
