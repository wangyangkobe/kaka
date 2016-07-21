# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from kaka.models import User, ShenQing, Machine, MachineUsage, QuanXian
from kaka import db, APPKEY, MASTERSECRET, APPID, Alias, HOST, logger
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
from datetime import datetime


from igetui import *
from igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.template.igt_apn_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *
from payload.APNPayload import SimpleAlertMsg
import os

user_blueprint = Blueprint('user', __name__)

push = IGeTui(HOST, APPKEY, MASTERSECRET)

# 透传模板动作内容
def TransmissionTemplateDemo(content):
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = content #'请填入透传内容'
    # iOS 推送需要的PushInfo字段 前三项必填，后四项可以填空字符串
    # template.setPushInfo(actionLocKey, badge, message, sound, payload, locKey, locArgs, launchImage)
    # template.setPushInfo("", 0, "", "com.gexin.ios.silence", "", "", "", "");

    # APN简单推送
    alertMsg = SimpleAlertMsg()
    alertMsg.alertMsg = ""
    apn = APNPayload();
    apn.alertMsg = alertMsg
    apn.badge = 2
    # apn.sound = ""
    apn.addCustomMsg("payload", "payload")
    # apn.contentAvailable=1
    # apn.category="ACTIONABLE"
    template.setApnInfo(apn)

    return template


def pushMessageToList(tokenList, template):
    # 消息模版： 
    # 1.TransmissionTemplate:透传功能模板  
    # 2.LinkTemplate:通知打开链接功能模板  
    # 3.NotificationTemplate：通知透传功能模板  
    # 4.NotyPopLoadTemplate：通知弹框下载功能模板

    # template = NotificationTemplateDemo()
    # template = LinkTemplateDemo()
    # template = TransmissionTemplateDemo()
    # template = NotyPopLoadTemplateDemo()

    message = IGtListMessage()
    message.data = template
    message.isOffline = True
    message.offlineExpireTime = 1000 * 3600 * 12
    message.pushNetWorkType = 0

    arr = []
    for token in tokenList:
        target = Target()
        target.appId = APPID
        target.clientId = token
        target.alias = Alias
        arr.append(target)
        
    contentId = push.getContentId(message)
    ret = push.pushMessageToList(contentId, arr)
    logger.info("pushMessageToList result = {}".format(ret))
    
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
    
    managerIds = [element.userId for element in QuanXian.query.all() if element.permission in [1, 2]]
    tokenList = filter(lambda x : len(x) > 0, [User.query.get(id).pushToken for id in managerIds])
    logger.info("managerIds = {}\ntokens ={}".format(managerIds, tokenList))
    pushMessageToList(tokenList, TransmissionTemplateDemo(applyDetail))
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
