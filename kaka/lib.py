# -*- coding: utf-8 -*-
from kaka import APPKEY, MASTERSECRET, APPID, Alias, HOST, logger



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

push = IGeTui(HOST, APPKEY, MASTERSECRET)

# 透传模板动作内容
def TransmissionTemplateDemo(content):
    template = TransmissionTemplate()
    template.transmissionType = 2
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = content #'请填入透传内容'
    # iOS 推送需要的PushInfo字段 前三项必填，后四项可以填空字符串
    # template.setPushInfo(actionLocKey, badge, message, sound, payload, locKey, locArgs, launchImage)
    # template.setPushInfo("", 0, "", "com.gexin.ios.silence", "", "", "", "");

    # APN简单推送
    alertMsg = SimpleAlertMsg()
    alertMsg.alertMsg = "兔乖乖"
    apn = APNPayload();
    apn.alertMsg = alertMsg
    apn.badge = 2
    # apn.sound = ""
    apn.addCustomMsg("payload", "payload")
    # apn.contentAvailable=1
    # apn.category="ACTIONABLE"
    template.setApnInfo(apn)
    
    logger.info("TransmissionTemplateDemo: transmissionContent={}".format(content))
    return template

def pushMessageToSingle(tokenList, template):    
    # 定义"SingleMessage"消息体，设置是否离线，离线有效时间，模板设置
    message = IGtSingleMessage()
    message.isOffline = True
    message.offlineExpireTime = 1000 * 3600 * 12
    message.data = template
    message.pushNetWorkType = 0#设置是否根据WIFI推送消息，2为4G/3G/2G,1为wifi推送，0为不限制推送
    target = Target()
    target.appId = APPID
    
    for token in tokenList:
        target.clientId = token
        try:
            ret = push.pushMessageToSingle(message, target)
            logger.info("pushMessageToSingle: token={}, result={}".format(token, ret))
        except RequestException, e:
            # 发生异常重新发送
            requstId = e.getRequestId()
            ret = push.pushMessageToSingle(message, target, requstId)
            logger.info("pushMessageToSingle: token={}, resend result={}".format(token, ret))

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

def formatTime(time):
	if time:
		return time.strftime("%Y-%m-%d %H:%M")
	else:
		return time

def getPassWordQuestion():
    questions = "您目前的姓名是?;您配偶的生日是?;您的学号（或工号）是?;您母亲的生日是?;您高中班主任的名字是?;您父亲的姓名是?;您小学班主任的名字是?;您父亲的生日是?;您配偶的姓名是?;您初中班主任的名字是?;您最熟悉的童年好友名字是?;您最熟悉的学校宿舍舍友名字是?;对您影响最大的人名字是?".split(";")
    res = list()
    for index, value in enumerate(questions, start=1):
        res.append({'id': index, 'question': value})
    return res