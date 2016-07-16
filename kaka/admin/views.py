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
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({"Mac"         : fields.Str(required=True),
                                       "MachineName" : fields.Str(required=True),
                                       "MachineType" : fields.Int(missing=0)}, required=True, many=True)
           },
          locations = ('json',))
@verify_request_token
def addMachines(args):
    userName = args.get("User", '')
    machines = request.get_json().get("Machines", [])
    user = models.User.getUserByUserName(userName)
    macAddesses = []
    try:
        for machine in machines:
            macAddress = machine.get('Mac')
            result = models.Machine.getMachineByMac(macAddress)
            if result:
                macAddesses.append(result.macAddress)
            else:
                machineName = machine.get("MachineName", '')
                machineType = machine.get("MachineType", 0)
                machineMoney= machine.get("MachineMoney", 0)
                adminPass   = machine.get("AdminPass", '')
                userPass    = machine.get("UserPass", '')
                result = models.Machine(macAddress, 
                                        machineName, 
                                        machineType  = machineType, 
                                        machineMoney = machineMoney, 
                                        adminPass    = adminPass, 
                                        userPass     = userPass)
                db.session.add(result)
                db.session.flush()
                macAddesses.append(result.macAddress)
        map(lambda address : db.session.merge(models.QuanXian(user.userName, address)), macAddesses)
        db.session.commit()
        
        return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200
    except Exception, error:
        return jsonify({'Status': 'Failed', 'StatusCode':-2, 'Msg': error.message}), 400


@admin_blueprint.route('/addUserPermission', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'UserPermissionList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                                 'User'       : fields.Str(required=True),
                                                 'Permission' : fields.Int(required=True)}, required=True, many=True)},
          locations = ('json',))
@verify_request_token
def addUserPermission(args):
    userPermissonList = request.get_json().get("UserPermissionList", [])
    errorDetail = []
    for userPermission in userPermissonList:
        userName   = userPermission.get('User')
        macAddress = userPermission.get('Mac')
        permission = userPermission.get('Permission')
        if not models.User.getUserByUserName(userName):
            errorDetail.append({'Status' :  'Success', 'StatusCode':0, 'Msg' : '用户{}不存在!'.format(userName)})
            break
        if not models.Machine.getMachineByMac(macAddress):
            errorDetail.append({'Status' :  'Success', 'StatusCode':0, 'Msg' : 'Mac{}不存在!'.format(userName)})
            break
        quanXians = models.QuanXian.query.filter_by(userId=userName, machineId=macAddress)
        if quanXians.count() == 0:
            db.session.add(models.QuanXian(userId=userName, machineId=macAddress, permission=permission))
        for quanXian in quanXians:
            quanXian.permission = permission
            db.session.merge(quanXian)
    db.session.commit()
    return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!', 'ErrorDetail': errorDetail}), 200

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
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'UserPermissionList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                                 'User'       : fields.Str(required=True),
                                                 'Permission' : fields.Int(required=True)}, required=True, many=True)},
          locations = ('json',))
@verify_request_token
def updateUserPermission(args):
    userPermissonList = request.get_json().get("UserPermissionList", [])
    for userPermission in userPermissonList:
        userName   = userPermission.get('User')
        macAddress = userPermission.get('Mac')
        permission = userPermission.get('Permission')
        if not models.User.getUserByUserName(userName):
            return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '用户{}不存在!'.format(userName)}), 400
        if not models.Machine.getMachineByMac(macAddress):
            return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : 'Mac{}不存在!'.format(userName)}), 400
        quanXians = models.QuanXian.query.filter_by(userId=userName, machineId=macAddress)
        if quanXians.count() == 0:
            return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '用户{}没有使用设备{}!'.format(userName, macAddress)}), 400
        for quanXian in quanXians:
            quanXian.permission = permission
            db.session.merge(quanXian)
    db.session.commit()
    return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200