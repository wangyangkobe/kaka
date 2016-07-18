# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args

admin_blueprint = Blueprint('admin', __name__)
    
@admin_blueprint.route('/addMachines', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({"Mac"         : fields.Str(required=True),
                                       "MachineName" : fields.Str(required=True),
                                       "MachineType" : fields.Int(missing=0)}, required=True)
           },
          locations = ('json',))
@verify_request_token
def addMachines(args):
    userId = args.get("UserId")
    user = models.User.query.get(userId)
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "UserId {} does't exist".format(userId)}), 400
    machine = request.get_json().get("Machines")
    print machine
    result = models.Machine.getMachineByMac(machine.get('Mac', ''))
    if not result:
        machine = models.Machine(**machine)
        db.session.add(machine)
        db.session.flush()
        db.session.add(models.QuanXian(user.id, machine.id, permission=1))
        db.session.commit()
        return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!', 'Machine': machine.toJson()}), 200
    else:
        return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作失败，改机器已被添加!'}), 400

@admin_blueprint.route('/addUserPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'UserList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                       'UserId'     : fields.Int(required=True),
                                       'Permission' : fields.Int(required=True)}, required=True)},
          locations = ('json',))
@verify_request_token
def addUserPermission(args):
    userList = request.get_json().get("UserList")
    userId = userList.get('UserId')
    user = models.User.query.get(userId)
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "UserId {} does't exist".format(userId)}), 400
    macAddress = userList.get('Mac', '')
    machine = models.Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    permisson = userList.get('Permission')
    quanXian = models.QuanXian(userId, machine.id, permission=permisson)
    db.session.merge(quanXian)
    db.session.commit()
    return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200
    
@admin_blueprint.route('/getUserLog', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'UserList' : fields.Nested({'User' : fields.Str(required=True)}, many=True, required=True)
           },
          locations = ('json',))
@verify_request_token
def getUserLog(args):
    userList = args.get('UserList')
    userLog = []
    for user in userList:
        if user.get('User') == 'All':
            userLog.extend([element.toJson() for element in models.QuanXian.query.all()])
        else:
            for quanXian in models.QuanXian.query.filter_by(userId=user.get('User')):
                userLog.append(quanXian.toJson())
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'UserLog': userLog})

@admin_blueprint.route('/getMachineLog', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'MacList'  : fields.Nested({'Mac' : fields.Str(required=True)}, many=True, required=True)
           },
          locations = ('json',))
@verify_request_token
def getMachineLog(args):
    macList = args.get('MacList')
    machineLog = []
    for mac in macList:
        if mac.get('Mac') == 'All':
            machineLog.extend([element.toJson() for element in models.QuanXian.query.all()])
        else:
            for quanXian in models.QuanXian.query.filter_by(machineId=mac.get('Mac')):
                machineLog.append(quanXian.toJson())
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'MachineLog': machineLog})

@admin_blueprint.route('/getMachinePermissionDetail', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'MacList'  : fields.Nested({'Mac' : fields.Str(required=True)}, many=True, required=True)
           },
          locations = ('json',))
@verify_request_token
def getMachinePermissionDetail(args):
    macList = args.get('MacList')
    permissonDetail = []
    for mac in macList:
        if mac.get('Mac') == 'All':
            for element in models.QuanXian.query.all():
                permissonDetail.append({'User': element.userId, 'Permission': element.permission, 'Mac': element.machineId})
        else:
            for element in models.QuanXian.query.filter_by(machineId=mac.get('Mac')):
                permissonDetail.append({'User': element.userId, 'Permission': element.permission, 'Mac': element.machineId})
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'PermissionDetail': permissonDetail})


@admin_blueprint.route('/updateUserPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'UserPermissionList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                                 'UserId'     : fields.Str(required=True),
                                                 'Permission' : fields.Int(required=True)}, required=True)},
          locations = ('json',))
@verify_request_token
def updateUserPermission(args):
    userPermissonList = request.get_json().get("UserPermissionList")
    userId = userPermissonList.get('UserId')
    user = models.User.query.get(userId)
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "UserId {} does't exist".format(userId)}), 400
    macAddress = userPermissonList.get('Mac', '')
    machine = models.Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    permisson = userPermissonList.get('Permission')
    quanXian = models.QuanXian(userId, machine.id, permission=permisson)
    db.session.merge(quanXian)
    db.session.commit()
    return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200