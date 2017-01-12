# -*- coding: utf-8 -*-
from kaka import db, logger
import datetime
from flask_login import UserMixin, make_secure_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.schema import PrimaryKeyConstraint
from webargs.core import ValidationError
import shortuuid, datetime, uuid

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    mysql_character_set = 'utf8'
    id           = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userName     = db.Column(db.String(80), nullable=False)
    passWord     = db.Column(db.String(80), nullable=True)
    phone        = db.Column(db.String(80), unique=False)
    email        = db.Column(db.String(80), unique=False)
    #userType     = db.Column(db.Integer,    nullable=False) # 0代表普通用户，1代表管理员，2代表超级管理员，3代表厂家
    verifyCode   = db.Column(db.String(80), unique=False)  #手机验证码
    pushToken    = db.Column(db.String(80))
    token        = db.Column(db.String(128))
    registerType = db.Column(db.Integer, unique=False) # 0为手机, 1为邮箱
    userMoney    = db.Column(db.Float)
    create_time  = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    passWordQA   = db.Column(db.String(100))

    nickName     = db.Column(db.String(50))
    headImage    = db.Column(db.String(200))
    logInType    = db.Column(db.Integer, default=0) #1为微信，2为qq，3 为微博，0 为账号密码
    logInToken   = db.Column(db.String(50))         #微信，qq，微博登陆对应的token

    quanXians   = db.relationship('QuanXian', cascade="all")

    def __init__(self, **kargs):
        logger.info('User __init__: kargs = {}'.format(kargs))
        self.userName = kargs.get('UserName', "")
        self.passWord = generate_password_hash(kargs.get('Password'))
        self.phone    = kargs.get('Phone', '')
        self.email    = kargs.get('Email', '')
        self.verifyCode = kargs.get('VerifyCode', '')
        self.pushToken  = kargs.get('PushToken', '')
        #self.userType   = kargs.get('UserType', 0)
        self.registerType = int(kargs.get('RegisterType', 0))
        self.userMoney   = kargs.get('UserMoney', 0.0)
        self.passWordQA  = kargs.get('PassWordQA', '')

        self.nickName   = kargs.get('NickName', '')
        self.headImage  = kargs.get('HeadImage', '')
        self.logInType  = kargs.get('LogInType', 0)
        self.logInToken = kargs.get('LogInToken', '')

    def verifyUser(self):
        if self.registerType == 0 and not self.phone:
            raise ValueError('手机注册，Phone不能为空!')
        if self.registerType == 1 and not self.email:
            raise ValueError('邮箱注册，Email不能为空!')
        if self.registerType==0 and User.query.filter_by(phone=self.phone).count() == 0:
            return True
        elif self.registerType==1 and User.query.filter_by(email=self.email).count() == 0:
            return True
        elif self.registerType==0:
            raise ValueError("The phone \"{}\" has been registered!".format(self.phone))
        else:
            raise ValueError("The email \"{}\" has been registered!".format(self.email))

    def checkPassWord(self, password):
        return check_password_hash(self.passWord, password)

    def get_auth_token(self):
        return uuid.uuid4().hex

    def updatePassWord(self, newPassWord):
        self.passWord = generate_password_hash(newPassWord)

    @staticmethod
    def checkUserToken(userid, token):
        return User.query.filter_by(id=userid, token=token).count() > 0
    @staticmethod
    def getUserByIdOrPhoneOrMail(id=None, phone=None, mail=None):
        if phone:
            user = User.query.filter_by(phone=phone).first()
            if user:
                return user;
            else:
                if id:
                    return User.query.get(id)
        elif id:
            return User.query.get(id)
        else:
            return None
    def toJson(self):
        result = dict((c.name, getattr(self, c.name)) for c in self.__table__.columns)
        if self.create_time:
            result['create_time'] = self.create_time.strftime("%Y-%m-%d %H:%M")
        return result

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

    def __init__(self, **kargs):
        self.macAddress   = kargs.get('Mac', "")
        self.machineName  = kargs.get('MachineName', "")
        self.machineType  = kargs.get('MachineType', 0)
        self.machineMoney = kargs.get('MachineMoney', 0.0)
        self.adminPass    = kargs.get('AdminPass', "")
        self.userPass     = kargs.get('UserPass', "")

    @staticmethod
    def getMachineByMac(macAddress):
        return Machine.query.filter_by(macAddress=macAddress).first()

    def toJson(self):
        return dict((c.name,
                     getattr(self, c.name))
                     for c in self.__table__.columns)

class QuanXian(db.Model):
    __tablename__  = 'user_machine'
    # 0是厂家，1是超级管理员，2是管理员，3是普通用户，4是访客，5是无权，6是匿名
    Producer, SuperAdmin, Admin, User, Vistor, NoRight, Anonymous = (0, 1, 2, 3, 4, 5, 6)
    #__table_args__ = (PrimaryKeyConstraint('userId', 'machineId'),)
    id         = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userId     = db.Column(db.Integer,  db.ForeignKey('user.id'))
    machineId  = db.Column(db.Integer, db.ForeignKey('machine.id', ondelete='CASCADE'))
    permission = db.Column(db.Integer, default=User)
    reason     = db.Column(db.String(200))
    startTime  = db.Column(db.DateTime)
    endTime    = db.Column(db.DateTime)
    money      = db.Column(db.Float, default=0.0)
    machineName= db.Column(db.String(200)) #用户对机器的命名

    def __init__(self, userId, machineId, permission=User,
                reason=None, startTime=None, endTime=None,
                money = 0, machineName=0):
        self.userId = userId
        self.machineId = machineId
        self.permission = permission
        self.reason = reason
        if startTime:
            self.startTime = startTime
        if endTime:
            self.endTime = endTime
        self.money = money
        self.machineName = machineName

    def toJson(self):
        result =  dict((c.name,
                        getattr(self, c.name))
                       for c in self.__table__.columns)
        if self.startTime:
            result['startTime'] = self.startTime.strftime("%Y-%m-%d %H:%M")
        if self.endTime:
            result['endTime']   = self.endTime.strftime("%Y-%m-%d %H:%M")
        return result

class ShenQing(db.Model):
    __tablename__  = 'shen_qing'
    id         = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userId     = db.Column(db.Integer, db.ForeignKey('user.id'))
    machineId  = db.Column(db.Integer, db.ForeignKey('machine.id', ondelete="CASCADE"))
    statusCode = db.Column(db.Integer, default=0)  #0代表管理员未查看该权限申请请求，-1表示拒绝该申请，1表示通过该申请
    needPermission = db.Column(db.Integer, default=0)
    reason     = db.Column(db.String(200))
    time       = db.Column(db.DateTime, default=datetime.datetime.utcnow) #申请的时间
    startTime  = db.Column(db.DateTime) # 开始使用该机器的时间
    endTime    = db.Column(db.DateTime) # 结束使用该机器的时间
    money      = db.Column(db.Float, default=0.0)

    def __init__(self, userId, machineId, statusCode=0, needPermission=-1,
                reason='', startTime=None, endTime=None, money=0.0,
                time=datetime.datetime.utcnow()):
        self.userId = userId
        self.machineId = machineId
        self.statusCode = statusCode
        self.needPermission = needPermission
        self.reason = reason
        self.time = time
        self.startTime = startTime
        self.endTime   = endTime
        self.money = money

    def toJson(self):
        result =  dict((c.name,
                        getattr(self, c.name))
                       for c in self.__table__.columns)
        if self.startTime:
            result['startTime'] = self.startTime.strftime("%Y-%m-%d %H:%M")
        if self.endTime:
            result['endTime']   = self.endTime.strftime("%Y-%m-%d %H:%M")
        return result

class MachineUsage(db.Model):
    __tablename__ = 'machine_usage'
    InfoUse, InfoStop = (0, 1)
    id         = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userId     = db.Column(db.Integer, db.ForeignKey('user.id'))
    machineId  = db.Column(db.Integer, db.ForeignKey('machine.id', ondelete="CASCADE"))
    action     = db.Column(db.String(20), nullable=True)  #0代表开始使用，1代表停止使用
    actiomTime = db.Column(db.DateTime)

    def __init__(self, userId, machineId, action=None, actionTime=datetime.datetime.utcnow()):
        self.userId = userId
        self.machineId = machineId
        self.action = action
        self.actiomTime = actionTime

    def toJson(self):
        result = dict( (c.name, getattr(self, c.name)) for c in self.__table__.columns )
        if self.actiomTime:
            result['actiomTime'] = self.actiomTime.strftime("%Y-%m-%d %H:%M")
        return result

class Address(db.Model):
    __tablename__ = 'address'
    id       = db.Column(db.BigInteger, autoincrement=True, nullable=False, primary_key=True)
    country  = db.Column(db.String(20))
    province = db.Column(db.String(20))
    city     = db.Column(db.String(20))
    district = db.Column(db.String(20))
    street   = db.Column(db.String(50))

    def __init__(self, **kargs):
        self.country  = kargs.get('Country', "")
        self.province = kargs.get('Province', "")
        self.city     = kargs.get('City', "")
        self.district = kargs.get('District', "")
        self.street   = kargs.get('Street', "")

    @staticmethod
    def getAddressId(place):
        (country, province, city, district, street) = place.split(',')
        address = Address.query.filter_by(country=country, province=province, city=city, district=district, street=street).first()
        if address:
            return address.id
        else:
            address = Address(Country=country, Province=province, City=city, District=district, Street=street)
            db.session.add(address)
            db.session.commit()
            db.session.flush()
            return address.id

    def toJson(self):
        result = dict((c.name, getattr(self, c.name)) for c in self.__table__.columns)
        return result

class Share(db.Model):
    __tablename__ = 'share'
    PriceHour, PriceDay, PriceMonth, PriceYear = (1, 2, 3, 4)
    Offline, Online = (0, 1)
    id          = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userId      = db.Column(db.Integer, db.ForeignKey('user.id'))
    #machineId   = db.Column(db.Integer, db.ForeignKey('machine.id', ondelete="CASCADE"))
    title       = db.Column(db.String(100))
    address     = db.Column(db.String(200))
    imageUrls   = db.Column(db.String(300))
    hotPointIds = db.Column(db.String(20))
    price       = db.Column(db.Float)
    priceUnit   = db.Column(db.Integer)   #表示价格是每次、每小时、每天等
    startTime   = db.Column(db.DateTime)
    endTime     = db.Column(db.DateTime)
    longitude	= db.Column(db.Float)
    latitude    = db.Column(db.Float)
    comments    = db.Column(db.String(200))
    usageInstruction = db.Column(db.String(200))
    shareCreateTime  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status      = db.Column(db.Integer, default=Online) #该分享“上线”或“下线”状态，有时候不想分享了，就下线。

    def __init__(self, **kargs):
        self.userId      = kargs.get("UserId")
        self.title       = kargs.get('Title', "")
        self.address     = kargs.get('Address', '').encode('utf-8')
        self.hotPointIds = kargs.get('HotPointIds', "")
        self.price       = kargs.get('Price', 0)
        self.priceUnit   = kargs.get('PriceUnit', 0)
        self.startTime   = kargs.get('StartTime', None)
        self.endTime     = kargs.get('EndTime', None)
        self.longitude   = kargs.get('Longitude', 0.0)
        self.latitude    = kargs.get('Latitude', 0.0)
        self.comments    = kargs.get('Comments', '')
        self.usageInstruction = kargs.get('UsageInstruction', "")
        self.status      = kargs.get('Status', Share.Online)
        self.imageUrls   = kargs.get('ImageUrls', "")

    def toJson(self):
        result = dict( (c.name, getattr(self, c.name)) for c in self.__table__.columns )
        if self.shareCreateTime:
            result['shareCreateTime'] = self.shareCreateTime.strftime("%Y-%m-%d %H:%M")
        if self.startTime:
            result['startTime'] = self.startTime.strftime("%Y-%m-%d %H:%M")
        if self.endTime:
            result['endTime'] = self.endTime.strftime("%Y-%m-%d %H:%M")  
        result['imageUrls'] = self.imageUrls.split(',')  
        return result

class Order(db.Model):
    __tablename__ = 'order'
    Init, WaitingPay, TradeDone, TradeClosed = (0, 1, 2, 3)
    orderId    = db.Column(db.String(30), nullable=False, primary_key=True)
    userId     = db.Column(db.Integer, db.ForeignKey('user.id'))
    shareId    = db.Column(db.Integer, db.ForeignKey('share.id', ondelete="CASCADE"))
    money      = db.Column(db.Float)
    status     = db.Column(db.Integer, default=Init)
    createTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, userId, shareId, money, status=Init, createTime=datetime.datetime.utcnow()):
        self.orderId = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S") + shortuuid.ShortUUID(alphabet="0123456789").random(length=10))
        self.userId  = userId
        self.shareId = shareId
        self.money   = money
        self.status  = status
        self.createTime = createTime

    def toJson(self):
        result = dict((c.name, getattr(self, c.name)) for c in self.__table__.columns)
        if self.createTime:
            result['createTime'] = self.createTime.strftime("%Y-%m-%d %H:%M")
        return result


class Comment(db.Model):
    __tablename__ = 'comment'
    id          = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    userId      = db.Column(db.Integer, db.ForeignKey('user.id'))
    shareId     = db.Column(db.Integer, db.ForeignKey('share.id', ondelete="CASCADE"))
    content     = db.Column(db.String(200))
    voteFlag    = db.Column(db.Integer, default=0)
    commentTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    score       = db.Column(db.Integer, default=0)
    imageUrl    = db.Column(db.String(100))

    def __init__(self, **kargs):
        self.userId   = kargs.get('UserId')
        self.shareId  = kargs.get("ShareId")
        self.content  = kargs.get('Content')
        self.voteFlag = kargs.get('VoteFlag', 0)
        self.score    = kargs.get('Score', 0)
        self.imageUrl = kargs.get('ImageUrl')
    def toJson(self):
        result = dict((c.name, getattr(self, c.name))
                          for c in self.__table__.columns)
        if self.shareCreateTime:
            result['commentTime'] = self.commentTime.strftime("%Y-%m-%d %H:%M")
        return result

class HotPoint(db.Model):
    __tablename__ = 'hotpoint'
    id          = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    name        = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(200))
    createBy    = db.Column(db.Integer, default=0) #创建热点的用户id：0表示系统实现定义好的，userId表示某个管理员添加的.

    def __init__(self, name, description="", createBy=0):
        self.name = name
        self.description = description
        self.createBy = createBy

    @staticmethod
    def checkExist(hotPointTag):
        result = HotPoint.query.filter_by(name=hotPointTag).first()
        if result:
            return result
        else:
            hotPoint = HotPoint(name = hotPointTag)
            db.session.add(hotPoint)
            db.session.commit()
            db.session.flush()
        return hotPoint


    def toJson(self):
        result = dict((c.name, getattr(self, c.name)) for c in self.__table__.columns)
        return result
