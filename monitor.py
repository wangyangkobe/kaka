#!/usr/bin/python
#coding: utf-8  
import smtplib  
from email.mime.text import MIMEText  
from email.header import Header  
from email.utils import parseaddr, formataddr
import logging
import requests
import os 

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger('monitor') 

sender     = 'wy250801860@163.com'  
receiver   = '2751530389@qq.com'
subject    = '兔乖乖服务器down机了!!!'  
smtpserver = 'smtp.163.com'  
username   = 'wy250801860@163.com'  
password   = 'Fuck250801860'  


def sendMail(content):  
    msg = MIMEText(content.encode('utf-8'),'plain','utf-8')   #中文需参数‘utf-8’，单字节字符不需要  
    msg['Subject'] = Header(subject, 'utf-8')  
    msg['from']    = sender
    msg['to']      = receiver
    try:  
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(1)  
        smtp.connect('smtp.163.com')  
        smtp.login(username, password)
        print msg
        print msg.as_string()  
        smtp.sendmail(sender, receiver, msg.as_string())  
        smtp.quit()  
        logger.info('send mail successfully!')
    except Exception:
        logger.info('send mail failed!')

developUrl = "https://139.224.3.149:5656/"
productUrl = "https://139.224.3.149:8080/api"

def checkServerStatus(url):
    try:
        response = requests.get(url, verify = False)
        if response.status_code == 200:
	    logger.info('check {} is ok!'.format(url))
            return True
        else:
            logger.info('check {} is not ok!'.format(url))
            return False
    except Exception:
       logger.info('check {} is not ok!'.format(url)) 
       return False    

if __name__ == '__main__':
    if not checkServerStatus(developUrl):
        sendMail(u"亲爱的管理员, 开发版服务器({})不可访问了，赶紧去看看吧!".format(developUrl))
    if not checkServerStatus(productUrl):
        sendMail(u"亲爱的管理员, 正式版服务器({})不可访问了，服务器已经开始重启!".format(productUrl))
        os.system("sudo reboot") 
