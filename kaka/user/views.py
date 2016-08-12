# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from kaka.models import User, ShenQing, Machine, MachineUsage, QuanXian
from kaka import db, logger
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
import json

from kaka.lib import TransmissionTemplateDemo, pushMessageToSingle
user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/applyPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(),
           'Phone'    : fields.Str(),
           'Token'    : fields.Str(required=True),
           'ApplyDetail' : fields.Nested({"Mac"         : fields.Str(required=True),
                                          "Permission"  : fields.Int(required=True, validate=lambda value: value in [0, 1, 2, 3]),
                                          'StartTime'   : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                          'EndTime'     : fields.DateTime(format='%Y-%m-%d %H:%M'),
                                          'Money'       : fields.Float(), 
                                          "Reason"      : fields.Str()}, required=True)
           },
          locations = ('json',))
@verify_request_token
def applyPermission(args):
    userId = args.get('UserId', '')
    phone  = args.get('Phone', '')
    user = User.getUserByIdOrPhoneOrMail(id=userId, phone=phone) 
    applyDetail = args.get('ApplyDetail')
    macAddress = applyDetail.get('Mac', '')
    startTime  = applyDetail.get('StartTime', '') if applyDetail.get('StartTime', '') else None
    endTime    = applyDetail.get('EndTime', '') if applyDetail.get('EndTime', '') else None
    money      = applyDetail.get('Money', 0.0)
    machine = Machine.query.filter_by(macAddress=macAddress).first()
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    
    needPermission = applyDetail.get('Permission')
    reason = applyDetail.get('Reason')
    shenQing = ShenQing(user.id, machine.id, reason=reason, needPermission=needPermission, startTime=startTime, endTime=endTime, money=money)
    db.session.add(shenQing)
    db.session.commit()
    
    managerIds = [element.userId for element in QuanXian.query.filter_by(machineId=machine.id) if element.permission in [1, 2]]
    tokenList = filter(lambda x : len(x) > 0, [User.query.get(id).pushToken for id in managerIds])
    logger.info("managerIds = {}\ntokens ={}".format(managerIds, tokenList))
    
    pushContent = request.get_json()
    pushContent.pop('Token', None)
    pushContent['UserName'] = user.userName
    pushContent['Phone'] = user.phone
    pushContent['Action'] = 'applyPermission'
    pushContent['ShenQingId'] = shenQing.id
    pushMessageToSingle(tokenList, TransmissionTemplateDemo( json.dumps(pushContent) ))
    
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '申请成功!', 'ApplyDetail': shenQing.toJson()}), 200

@user_blueprint.route('/infoUseMachine', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Mac'      : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def infoUseMachine(args):
    macAddress = args.get('Mac', '')
    userId     = args.get('UserId')
    machine    = Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    machineUsage = MachineUsage(userId=userId, machineId=machine.id, action=MachineUsage.InfoUse)
    db.session.add(machineUsage)
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200


@user_blueprint.route('/infoStopUseMachine', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Mac'      : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def infoStopUseMachine(args):
    macAddress = args.get('Mac', '')
    userId     = args.get('UserId')
    machine    = Machine.getMachineByMac(args.get('Mac', ''))
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    
    machineUsage = MachineUsage(userId=userId, machineId=machine.id, action=MachineUsage.InfoStop)
    db.session.add(machineUsage)
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200

@user_blueprint.route('/queryApplyings', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           #'Machines' : fields.Nested({"Mac" : fields.Str(required=True)}, require=True, many=True)
           },
          locations = ('json',))
@verify_request_token
def queryApplyings(args):
    userId = args.get('UserId')
    result = []
    for shenQing in ShenQing.query.filter_by(userId=userId):
        content = shenQing.toJson()
        machine = Machine.query.get(shenQing.machineId)
        content['machineName'] = machine.machineName
        content['mac'] = machine.macAddress
        result.append(content)
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'Applyings': result}), 200

@user_blueprint.route('/infoOperateMachine', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Action'   : fields.Str(required=True),
           'Mac'      : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def infoOperateMachine(args):
    macAddress = args.get('Mac', '')
    userId     = args.get('UserId')
    action     = args.get('Action')
    machine    = Machine.getMachineByMac(macAddress)
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    if action not in ['Use', 'Stop']:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "无效的action \"{}\"".format(action)}), 400
    machineUsage = MachineUsage(userId=userId, machineId=machine.id, action=action)
    db.session.add(machineUsage)
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200

@user_blueprint.route('/getMyPermissionDetail', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'MacList'  : fields.Nested({'Mac' : fields.Str(required=True)}, required=True, many=True)},
          locations = ('json',))
@verify_request_token
def getMyPermissionDetail(args):
    macList = request.get_json().get('MacList', [])
    userId  = args.get('UserId')
    result  = []
    for mac in macList:
        if mac.get('Mac') == 'All':
            for quanXian in QuanXian.query.filter_by(userId=userId):
                machine = Machine.query.get(quanXian.machineId)
                result.append({'Permission': quanXian.permission, 'Machine': machine.toJson()})
        else:
            mac     = mac.get('Mac')
            machine = Machine.query.filter_by(macAddress=mac).first()
            if not machine:
                return jsonify({'Status': 'Failded', 'StatusCode': -1, 'Msg': '操作失败, 无法查看机器{}!'.format(mac)}), 400
            for quanXian in QuanXian.query.filter_by(userId=userId, machineId=machine.id):
                result.append({'Permission': quanXian.permission, 'Machine': machine.toJson()})
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'PermissionDetail': result}), 200
