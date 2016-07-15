# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields, validate
from webargs.flaskparser import use_args
from webargs.core import ValidationError

api_blueprint = Blueprint('api', __name__)
 
def validateUserType(value):
    if  value >=0 and value <=3:
        return True
    else:
        raise ValidationError('The userType field is {}, should be 0,1,2,3'.format(value))
    
@api_blueprint.route('/', methods=['GET'])
def test():
    return "Hello world!"
    
@api_blueprint.route('/register', methods=['POST'])
@verify_request_json
@use_args({'User'       : fields.Str(required=True),
           'Password'   : fields.Str(required=True),
           'UserType'   : fields.Int(required=True, missing=1, validate=validateUserType),
           'RegisterTye': fields.Int(required=True, missing=0)},
          locations = ('json',))
def register(args):
    userName     = request.json.get('User', '')
    passWord     = request.json.get('Password', '')
    phone        = request.json.get('Phone', '')
    email        = request.json.get('Email', '')
    code         = request.json.get('Code', '')
    pushToken    = request.json.get('PushToken', '')
    userType     = args['UserType']  
    registerType = args['RegisterTye']
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
@use_args({'User'     : fields.Str(required=True),
           'Password' : fields.Str(required=True)},
          locations = ('json',))
def login(args):
    userName = args['User']
    passWord = args['Password']
    
    user = models.User.getUserByUserName(userName)
    if user:
        if user.checkPassWord(passWord):
            user.token = user.get_auth_token()
            user.pushToken = request.json.get('PushToken', '')
            db.session.merge(user)
            db.session.commit()
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
