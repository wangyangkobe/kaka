# -*- coding: utf-8 -*-
from kaka import db
import datetime
from flask_login import UserMixin, make_secure_token
from werkzeug.security import generate_password_hash, check_password_hash

quanxian_table = db.Table('quanxian',
    db.Column('userId', db.Integer, db.ForeignKey('user.id')),
    db.Column('machineId', db.Integer, db.ForeignKey('machine.id')),
    db.Column('permission', db.Integer),
    db.Column('reason', db.String(200)),
    db.Column('startTime', db.DateTime, default=datetime.datetime.utcnow),
    db.Column('endTime', db.DateTime),
    db.Column('money', db.Float),
    db.Column('machineName', db.String(200)), #用户对机器的命名
    db.PrimaryKeyConstraint('userId', 'machineId')
    )
    
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName    = db.Column(db.String(80), unique=True, nullable=False)
    passWord    = db.Column(db.String(80), nullable=False)
    phone       = db.Column(db.String(80), unique=True)
    email       = db.Column(db.String(80), unique=True)
    userType    = db.Column(db.Integer, nullable=False)
    code        = db.Column(db.String(80), unique=False)
    pushToken   = db.Column(db.String(80))
    token       = db.Column(db.String(128))
    regiserType = db.Column(db.Integer, unique=False)
    userMoney   = db.Column(db.Float)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    def __init__(self, username, password, phone = None, email = None, code = None, pushToken = None, userType = 0, registerType = 0, userMoney = 0.0):
        self.userName = username
        self.passWord = generate_password_hash(password)
        self.phone = phone
        self.email = email
        self.code = code
        self.pushToken = pushToken
        self.userType = userType
        self.regiserType = registerType
        self.userMoney = userMoney
    
    def verifyUser(self):
        if self.regiserType == 0 and not self.phone:
            raise ValueError('手机注册，Phone不能为空!')
        if self.regiserType == 1 and not self.email:
            raise ValueError('邮箱注册，Email不能为空!')
        return True
    
    def checkPassWord(self, password):
        return check_password_hash(self.passWord, password)
    
    def get_auth_token(self):
        return make_secure_token(self.userName, key='deterministic')
    
    @staticmethod
    def getUserByUserName(username):
        return User.query.filter_by(userName=username).first()
    
    @staticmethod
    def checkUserToken(username, token):
        return User.query.filter_by(userName=username, token=token).count() > 0
    
    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)
        
class Machine(db.Model):
    __tablename__ = 'machine'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    macAddress  = db.Column(db.String(100), nullable=False, unique=True)
    machineName = db.Column(db.String(100), nullable=False) #机器出厂时的设备名
    machineType = db.Column(db.Boolean, nullable=False, default=False) #指定设备为“可匿名访问” 
    machineMoney= db.Column(db.Float)
    adminPass   = db.Column(db.String(100)) #管理员密码
    userPass    = db.Column(db.String(100)) #用户密码
    
    def __init__(self, macAddress, machineName):
        self.macAddress = macAddress
        self.machineName = machineName
        
    @staticmethod
    def getMachineByMac(macAddress):
        return Machine.query.filter_by(macAddress=macAddress).first()
        