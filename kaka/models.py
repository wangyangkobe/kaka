# -*- coding: utf-8 -*-
from kaka import db
import datetime
from flask_login import UserMixin, make_secure_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.schema import PrimaryKeyConstraint
from webargs.core import ValidationError
    
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id           = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userName     = db.Column(db.String(80), nullable=False)
    passWord     = db.Column(db.String(80), nullable=False)
    phone        = db.Column(db.String(80), unique=True)
    email        = db.Column(db.String(80), unique=True)
    userType     = db.Column(db.Integer,    nullable=False)
    verifyCode   = db.Column(db.String(80), unique=False)
    pushToken    = db.Column(db.String(80))
    token        = db.Column(db.String(128))
    registerType = db.Column(db.Integer, unique=False)
    userMoney    = db.Column(db.Float)
    create_time  = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    quanXians   = db.relationship('QuanXian', cascade="all")
    
    def __init__(self, **kargs):
        print kargs
        self.userName = kargs.get('UserName', "")
        self.passWord = generate_password_hash(kargs.get('Password'))
        self.phone    = kargs.get('Phone', '')
        self.email    = kargs.get('Email', '')
        self.verifyCode = kargs.get('VerifyCode', '')
        self.pushToken  = kargs.get('PushToken', '')
        self.userType   = kargs.get('UserType', 0)
        self.registerType = kargs.get('RegisterType', 0)
        self.userMoney   = kargs.get('UserMoney', 0.0)
        
    def verifyUser(self):
        if self.registerType == 0 and not self.phone:
            raise ValueError('手机注册，Phone不能为空!')
        if self.registerType == 1 and not self.email:
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
    
    @staticmethod
    def checkUserNameExist(userName):
        if User.getUserByUserName(userName):
            return True
        else:
            raise ValidationError("The user \"{}\" don't exist!".format(userName))
    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)
        
class Machine(db.Model):
    __tablename__ = 'machine'
    id          = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    macAddress  = db.Column(db.String(100), nullable=False, unique=True)
    machineName = db.Column(db.String(100), nullable=False) #机器出厂时的设备名
    machineType = db.Column(db.Integer, nullable=False, default=0) #指定设备为“可匿名访问” 
    machineMoney= db.Column(db.Float)
    adminPass   = db.Column(db.String(100)) #管理员密码
    userPass    = db.Column(db.String(100)) #用户密码
    
    #users = db.relationship("QuanXian", back_populates="user")
    quanXians   = db.relationship('QuanXian', cascade="all, delete-orphan")
    
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
    userId     = db.Column(db.Integer,  db.ForeignKey('user.id'))
    machineId  = db.Column(db.Integer, db.ForeignKey('machine.id', ondelete='CASCADE'))
    permission = db.Column(db.Integer, default=0) #0代表管理员未查看该权限申请请求，1代表已经询问管理员，2代表管理员已经处理
    reason     = db.Column(db.String(200))
    startTime  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    endTime    = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    money      = db.Column(db.Float, default=0.0)
    machineName= db.Column(db.String(200)) #用户对机器的命名
 
    def __init__(self, userId, machineId, permission=0, reason=None, startTime=datetime.datetime.utcnow(), endTime=datetime.datetime.utcnow(), money = 0, machineName=0):
        self.userId = userId
        self.machineId = machineId
        self.permission = permission
        self.reason = reason
        self.startTime = startTime
        self.endTime = endTime
        self.money = money
        self.machineName = machineName
        
    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)