# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka.models import User, Machine, QuanXian
from kaka import db, logger
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
from webargs.core import ValidationError
from kaka.lib import TransmissionTemplateDemo, pushMessageToSingle
import json

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
@use_args({'UserName'    : fields.Str(required=True),
           'Password'    : fields.Str(required=True),
           #'UserType'    : fields.Int(required=True, missing=1, validate=validateUserType),
           'RegisterType': fields.Int(required=True, missing=0, validate=lambda value : value in [0, 1])},
          locations = ('json',))
def register(args):
    try:
        user = User(**request.get_json())
        user.verifyUser()
        db.session.add(user)
        db.session.commit()
        return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '注册成功!', 'User': user.toJson()}), 200
    except ValueError, error:
        logger.info('ValueError: errorMsg = {}'.format(error.message))
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': error.message}), 400
    except Exception, error:
        logger.info('Exception: errorMsg = {}'.format(error.message))
        return jsonify({'Status': 'Failed', 'StatusCode': -2, 'Msg': error.message}), 400
    
@api_blueprint.route('/login', methods=['POST'])
@verify_request_json
@use_args({'Password'     : fields.Str(required=True),
           'Phone'        : fields.Str(missing=''),
           'Email'        : fields.Str(missing=''),
           'RegisterType' : fields.Int(required=True, validate=lambda value : value in [0, 1])},
          locations = ('json',))
def login(args):
    passWord = args['Password']
    registerType = args['RegisterType']
    phone = args['Phone']
    email = args['Email']
    if registerType == 0 and not phone:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': "Phone不能为空!"}), 400
    if registerType == 1 and not email:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': "Email不能为空!"}), 400
    if registerType == 0:
        user = User.query.filter_by(phone=phone).first()
    else:
        user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '输入的Phone或Email不存在!'}), 400
    oldPushToken = user.pushToken if user else ''
    if user.checkPassWord(passWord):
        user.token = user.get_auth_token()
        user.pushToken = request.json.get('PushToken', '')
        db.session.merge(user)
        db.session.commit()
        userJson = user.toJson()
        userJson.pop('passWord', None),

        if oldPushToken and oldPushToken != user.pushToken:
            pushContent = {'Phone': phone, 'Action': 're-loggin', 'Msg': u'user change phone to re-loggin'}
            pushMessageToSingle([oldPushToken], TransmissionTemplateDemo( json.dumps(pushContent) ))

        return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '登录成功!', 'User': userJson}), 200
    else:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '密码错误'}), 400 

@api_blueprint.route('/logout', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True)},
          locations = ('json',))
def logout(args):
    user = User.query.get(args.get('UserId'))
    user.pushToken = ""
    user.token = ""
    db.session.merge(user)
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '注销成功!'}), 200  
    
def verifyMachines(machines):
    if isinstance(machines, list):
        for machine in machines:
            if isinstance(machine, dict) and machine.has_key('Mac'):
                return True
            else:
                raise ValidationError('输入的Machines字符不正确 ！')
    else:
        raise ValidationError('输入的Machines字符不正确 ！')
    
@api_blueprint.route('/delMachines',  methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({'Mac' : fields.Str(require=True)}, required=True, many=True)},
          locations = ('json',))
@verify_request_token
def delMachines(args):
    user = User.query.get(args.get('UserId'))
    machines = args.get('Machines', [])
    for machine in machines:
        macAddress = machine.get('Mac')
        if macAddress == 'All':
            for quanXian in user.quanXians:
                if quanXian.permission in [3,4,5,6]:
                    pass
                else:
                    Machine.query.filter_by(id=quanXian.machineId).delete()
        else:
            machine = Machine.query.filter_by(macAddress=macAddress).first()
            if not machine:
                return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '操作失败,机器{}不存在!'.format(macAddress)}), 400 
            if QuanXian.query.filter(QuanXian.userId==user.id).filter(QuanXian.machineId==machine.id).filter(QuanXian.permission.in_( (0,1,2) )):
                Machine.query.filter_by(id=machine.id).delete()
            else:
                return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '您是普通用户,无权删除机器{}!'.format(macAddress)}), 400 
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200   
                
