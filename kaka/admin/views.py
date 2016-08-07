# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka.models import User, Machine, QuanXian, MachineUsage, ShenQing
from kaka import db, logger
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
from kaka.lib import TransmissionTemplateDemo, pushMessageToSingle

admin_blueprint = Blueprint('admin', __name__)
    
@admin_blueprint.route('/addMachines', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(),
           'Phone'    : fields.Str(),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({"Mac"         : fields.Str(required=True),
                                       "MachineName" : fields.Str(required=True),
                                       "MachineType" : fields.Int(missing=0)}, required=True)
           },
          locations = ('json',))
@verify_request_token
def addMachines(args):
    userId = args.get("UserId", '')
    phone  = args.get('Phone', '')
    user = User.getUserByIdOrPhoneOrMail(id=userId, phone=phone)
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "UserId {} does't exist".format(userId)}), 400
    machine = request.get_json().get("Machines")
    result = Machine.getMachineByMac(machine.get('Mac', ''))
    if not result:
        machine = Machine(**machine)
        db.session.add(machine)
        db.session.flush()
        db.session.add(QuanXian(user.id, machine.id, permission=1))
        db.session.commit()
        return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!', 'Machine': machine.toJson()}), 200
    else:
        return  jsonify({'Status' :  'Failed', 'StatusCode':-1, 'Msg' : '操作失败，改机器已被添加!'}), 400

@admin_blueprint.route('/addUserPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(),
           'Phone'    : fields.Str(), 
           'Token'    : fields.Str(required=True),
           'UserList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                       'UserId'     : fields.Int(required=True),
                                       'StartTime'  : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                       'EndTime'    : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                       'Money'      : fields.Float(), 
                                       'Permission' : fields.Int(required=True, validate=lambda value: value in [0, 1, 2, 3])}, required=True)},
          locations = ('json',))
@verify_request_token
def addUserPermission(args):
    userId = args.get('UserId', '')
    phone  = args.get('Phone', '')
    token  = args.get('Token', '')
    user   = User.getUserByIdOrPhoneOrMail(id=userId, phone=phone)  
    userList = request.get_json().get("UserList")
    userId   = user.id
    macAddress = userList.get('Mac', '')
    machine    = Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    
    permisson = userList.get('Permission')
    startTime  = userList.get('StartTime', None) 
    endTime    = userList.get('EndTime', None) 
    money      = userList.get('Money', 0.0)
    
    quanXian = QuanXian(userId, machine.id, permission=permisson, startTime=startTime, endTime=endTime, money=money)
    db.session.merge(quanXian)
    db.session.commit()
    
    pushContent = {'Action': 'addUserPermission', 'Permission': permisson, 'Mac': macAddress, 'StartTime': startTime, 'EndTime': endTime, 'Money': money}
    pushMessageToSingle([user.pushToken], TransmissionTemplateDemo(pushContent))
    
    return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200


@admin_blueprint.route('/updateUserPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(),
           'Phone'    : fields.Str(),
           'Token'    : fields.Str(required=True),
           'UserPermissionList' : fields.Nested({'Mac'        : fields.Str(required=True),
                                                 'UserId'     : fields.Int(required=True),
						 'StartTime'  : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                                 'EndTime'    : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                                 'Money'      : fields.Float(),
                                                 'Permission' : fields.Int(required=True, validate=lambda value: value in [0, 1, 2, 3])}, required=True)},
          locations = ('json',))
@verify_request_token
def updateUserPermission(args):
    userPermissonList = request.get_json().get("UserPermissionList")
    userId = userPermissonList.get('UserId')
    user = User.query.get(userId)
    if not user:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "UserId {} does't exist".format(userId)}), 400
    macAddress = userPermissonList.get('Mac', '')
    machine = Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    permission = userPermissonList.get('Permission')
    startTime  = userPermissonList.get('StartTime', None) 
    endTime    = userPermissonList.get('EndTime', None)
    money      = userPermissonList.get('Money', -1)

    quanXian = QuanXian.query.filter_by(userId=userId, machineId=machine.id).order_by('id desc').first()
    quanXian.permission = permission
    if not quanXian:
	      return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "User {} don't use machine {}".format(userId, macAddress)}), 400
    if money != -1:
        quanXian.money = money
    if startTime != None:
        quanXian.startTime = startTime
    if endTime != None:
        quanXian.endTime = endTime

    print quanXian.permission, quanXian.id, quanXian.startTime
    db.session.merge(quanXian)
    db.session.commit()
    
    pushContent = {'Action': 'updateUserPermission', 'Permission': permission, 'Mac': macAddress, 'Money':money, 'StartTime':startTime, 'EndTime':endTime}
    pushMessageToSingle([user.pushToken], TransmissionTemplateDemo(pushContent))
    
    return jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'}), 200


@admin_blueprint.route('/getMachineLog', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'MacList'  : fields.Nested({'Mac' : fields.Str(required=True)}, many=True, required=True)
           },
          locations = ('json',))
@verify_request_token
def getMachineLog(args):
    macList = args.get('MacList')
    manageMachines = []
    for quanXian in QuanXian.query.filter(userId=args.get('UserId')):
        if quanXian.permission != 0:
            manageMachines.append(quanXian.machineId)
    machineLog = []
    for mac in macList:
        if mac.get('Mac') == 'All':
            machineLog.extend([element.toJson() for element in MachineUsage.query.all() if element.machineId in manageMachines])
        else:
            machine = Machine.query.filter_by(macAddress=mac.get('Mac')).first()
            if machine:
                for machineUsage in MachineUsage.query.filter_by(machineId=machine.id):
                    if machineUsage.machieId in manageMachines:
                        machineUsage = machineUsage.toJson()
                        machineUsage.pop('id', None)
                        machineLog.append(machineUsage)
            else:
                return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(mac.get('Mac'))}), 400
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'MachineLog': machineLog}), 200


@admin_blueprint.route('/getNewRequest', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def getNewRequest(args):
    requestList = []
    for shenQing in ShenQing.query.filter_by(statusCode=0):
        result = shenQing.toJson()
        result.pop('id', None)
        requestList.append(result)
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'Request': requestList}), 200


@admin_blueprint.route('/getMachinePermissionDetail', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'PhoneList': fields.Nested({'Phone' : fields.Str(required=True)}, required=True),
           'MacList'  : fields.Nested({'Mac'   : fields.Str(required=True)}, many=True, required=True)
           },
          locations = ('json',))
@verify_request_token
def getMachinePermissionDetail(args):
    userId = args.get('UserId')
    phone  = args.get('PhoneList').get('Phone')
    ownMachines = QuanXian.query.filter(QuanXian.userId == userId).filter(QuanXian.permission != 0)
    ownMachineIds = [element.machineId for element in ownMachines]
    userIds = []
    if phone == 'All':
        userIds = [user.id for user in User.query.all()]
    else:
        userIds = [user.id for user in User.query.filter_by(phone=phone)]
    logger.info("getMachinePermissionDetail ownMachineIds = {}".format(ownMachineIds))
    if not ownMachineIds:
        return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,您还不是任何机器的管理员!'}), 400

    macList = args.get('MacList')
    permissonDetail = []
    for mac in macList:
        if mac.get('Mac') == 'All':
            for element in QuanXian.query.filter(QuanXian.machineId.in_(ownMachineIds)):
                if element.userId not in userIds:
                    continue
                user = User.query.get(element.userId)
                userJson = user.toJson()
                userJson.pop('passWord', None)
                userJson.pop('token', None)
                machine = Machine.query.get(element.machineId)
                permissonDetail.append({'User': userJson, 'Permission': element.permission, 'Machine': machine.toJson()})
        else:
            machine = Machine.query.filter_by(macAddress=mac.get('Mac')).first()
            if not machine:
                return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,机器{}不存在!'.format(mac.get('Mac'))}), 400
            if machine.id not in ownMachineIds:
                return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,您不是机器{}的管理员!'.format(mac.get('Mac'))}), 400
            for element in QuanXian.query.filter_by(machineId=machine.id):
                if element.userId not in userIds:
                    continue
                user = User.query.get(element.userId)
                userJson = user.toJson()
                userJson.pop('passWord', None)
                userJson.pop('token', None)
                machine = Machine.query.get(element.machineId)
                permissonDetail.append({'User': userJson, 'Permission': element.permission, 'Machine': machine.toJson()})
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'PermissionDetail': permissonDetail}), 200

    
@admin_blueprint.route('/getUserLog', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def getUserLog(args):
    userList = request.get_json().get('UserList', [])
    userLog = []
    for user in userList:
        if user.get('UserId') == 'All':
            userLog.extend([element.toJson() for element in MachineUsage.query.all()])
        else:
            if not User.query.get(user.get('UserId')):
                return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,用户id={}不存在!'.format(user.get('UserId'))}), 400
            for machineUsage in MachineUsage.query.filter_by(userId=user.get('UserId')):
                machineUsage = machineUsage.toJson()
                machineUsage.pop('id', None)
                userLog.append(machineUsage)
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'UserLog': userLog}), 200

@admin_blueprint.route('/getUserDetailInfo', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'UserList' : fields.Nested({'UserId' : fields.Integer(),
                                        'Phone' : fields.Str()}, required=True)},
          locations = ('json',))
@verify_request_token
def getUserDetailInfo(args):
    userList = request.get_json().get('UserList')
    userId   = userList.get('UserId', '')
    phone    = userList.get('Phone', '')
    user     = User.getUserByIdOrPhoneOrMail(id=userId, phone=phone)
    userJson = user.toJson()
    userJson.pop('passWord', None)
    if user:
        return  jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'UserInfo': userJson}), 200
    else:
        return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,用户id={}不存在!'.format(userId)}), 400


@admin_blueprint.route('/getMachineDetailInfo', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'MacList'  : fields.Nested({'Mac' : fields.Str(required=True)}, required=True)},
          locations = ('json',))
@verify_request_token
def getMachineDetailInfo(args):
    logger.info("getMachineDetailInfo: request json = {}".format(request.get_json()))
    macList = request.get_json().get('MacList')
    mac     = macList.get('Mac')
    machine = Machine.query.filter_by(macAddress=mac).first()
    if machine:
        return  jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'MachineInfo': machine.toJson()}), 200
    else:
        return jsonify({'Status': 'Success', 'StatusCode': -1, 'Msg': '操作失败,机器mac={}不存在!'.format(mac)}), 400
