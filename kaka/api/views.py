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
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({'Mac' : fields.Str(require=True)}, validate=verifyMachines, many=True)},
          locations = ('json',))
@verify_request_token
def delMachines(args):
    user = models.User.getUserByUserName(args.get('User', ''))
    for machine in args.get('Machines'):
        if machine.get('Mac') == "All":
            for quanxian in user.quanXians:
                machines = models.Machine.query.filter_by(macAddress=quanxian.machineId)
                map(lambda machine : db.session.delete(machine), machines)
        else:
            for quanxian in models.QuanXian.query.filter_by(userId=user.userName, machineId=machine.get('Mac')):
                machines = models.Machine.query.filter_by(macAddress=quanxian.machineId)
                map(lambda machine : db.session.delete(machine), machines)
                print quanxian.machineId
        db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200
        
    print args
    if args.get('Machines') == 'All':
        print user.quanXians
        map(lambda machine : db.session.delete(machine), user.machines)
    else:
        needDeletes = request.get_json().get("Machines", [])
        print needDeletes
        result = [i for i in user.machines for j in needDeletes if i.macAddress == j['mac']]
        map(lambda machine : db.session.delete(machine), result)
    db.session.commit()
    return jsonify(user.toJson())
