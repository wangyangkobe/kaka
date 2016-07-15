# -*- coding: utf-8 -*-
from kaka import db
import datetime
from flask_login import UserMixin, make_secure_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.schema import PrimaryKeyConstraint
    
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
    machines    = db.relationship('Machine',secondary='user_machine',backref=db.backref('user', lazy='dynamic'),lazy='dynamic')
    
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
    machineType = db.Column(db.Integer, nullable=False, default=0) #指定设备为“可匿名访问” 
    machineMoney= db.Column(db.Float)
    adminPass   = db.Column(db.String(100)) #管理员密码
    userPass    = db.Column(db.String(100)) #用户密码
    
    #users = db.relationship("QuanXian", back_populates="user")
    
    def __init__(self, macAddress, machineName, machineType=0, machineMoney=0.0, adminPass=None, userPass=None):
        self.macAddress   = macAddress
        self.machineName  = machineName
        self.machineType  = machineType
        self.machineMoney = machineMoney
        self.adminPass    = adminPass
        self.userPass     = userPass
        
    @staticmethod
    def getMachineByMac(macAddress):
        return Machine.query.filter_by(macAddress=macAddress).first()
    
    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)
        
class QuanXian(db.Model):
    __tablename__  = 'user_machine'
    __table_args__ = (PrimaryKeyConstraint('userId', 'machineId'),)
    userId     = db.Column(db.Integer, db.ForeignKey('user.id'))
    machineId  = db.Column(db.Integer, db.ForeignKey('machine.id'))
    permission = db.Column(db.Integer)
    reason     = db.Column(db.String(200))
    startTime  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    endTime    = db.Column(db.DateTime)
    money      = db.Column(db.Float)
    machineName= db.Column(db.String(200)) #用户对机器的命名
 
    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)