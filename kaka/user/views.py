# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from kaka.models import User, QuanXian, ShenQing, Machine, MachineUsage
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
from datetime import datetime

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/applyPermission', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'ApplyDetail' : fields.Nested({"Mac"         : fields.Str(required=True),
                                          "Permission"  : fields.Int(required=True, validate=lambda value: value in [0, 1, 2, 3]),
                                          "Reason"      : fields.Str()}, required=True)
           },
          locations = ('json',))
@verify_request_token
def applyPermission(args):
    user = User.query.get(args['UserId'])
    applyDetail = args.get('ApplyDetail')
    macAddress = applyDetail.get('Mac', '')
    machine = Machine.query.filter_by(macAddress=macAddress).first()
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    
    needPermission = applyDetail.get('Permission')
    reason = applyDetail.get('Reason')
    shenQing = ShenQing(user.id, machine.id, reason=reason, needPermission=needPermission)
    db.session.add(shenQing)
    db.session.commit()
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '申请成功!', 'ApplyDetail': shenQing.toJson()}), 200

@user_blueprint.route('/infoUseMachine', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Mac'      : fields.Str(required=True)},
          locations = ('json',))
@verify_request_token
def infoUseMachine(args):
    machine = Machine.getMachineByMac(args.get('Mac', ''))
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    machineUsage = MachineUsage.query.filter_by(userId=args.get('UserId'), machineId=machine.id).first()
    if machineUsage:
        machineUsage.startTime=datetime.utcnow() 
        db.session.merge(machineUsage)
    else:
        db.session.add(MachineUsage(userId=args.get('UserId'), machineId=machine.id, startTime=datetime.utcnow()))
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
    machine = Machine.getMachineByMac(args.get('Mac', ''))
    if not machine:
        return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
    machineUsage = MachineUsage.query.filter_by(userId=args.get('UserId'), machineId=machine.id).first()
    if machineUsage:
        machineUsage.endTime=datetime.utcnow() 
        db.session.merge(machineUsage)
        db.session.commit()
        return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!'}), 200
    else:
        return jsonify({'Status': 'Failed', 'StatusCode': -1, 'Msg': '您还为使用该机器!'}), 400

@user_blueprint.route('/queryMachines', methods=['POST'])
@verify_request_json
@use_args({'UserId'   : fields.Int(required=True),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({"Mac" : fields.Str(required=True)}, require=True, many=True)
           },
          locations = ('json',))
@verify_request_token
def queryMachines(args):
    userId = args.get('UserId')
    machineList = args.get('Machines', [])
    result = []
    for element in machineList:
        macAddress = element.get('Mac', '')
        machine = Machine.getMachineByMac(macAddress)
        if not machine:
            return jsonify({'Status': 'Failed', 'StatusCode':-1, 'Msg': "MacAddress {} does't exist".format(macAddress)}), 400
        for shenQing in ShenQing.query.filter_by(userId=userId, machineId=machine.id):
            result.append({'Mac': macAddress, 'Permission': shenQing.needPermission, 'StatusCode': shenQing.statusCode})
    return jsonify({'Status': 'Success', 'StatusCode': 0, 'Msg': '操作成功!', 'PermissionResult': result}), 200
