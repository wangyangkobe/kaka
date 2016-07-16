# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args

admin_blueprint = Blueprint('admin', __name__)

    
@admin_blueprint.route('/addMachines', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=models.User.checkUserNameExist),
           'Token'    : fields.Str(required=True),
           'Machines' : fields.Nested({'mac'         : fields.Str(require=True),
                                       'MachineName' : fields.Str(require=True)}, many=True),
           'machineType' : fields.Int(missing=0)
           },
          locations = ('json',))
@verify_request_token
def addMachines(args):
    userName = args.get("User", '')
    machines = request.get_json().get("Machines", [])
    user = models.User.getUserByUserName(userName)
    macAddesses = []
    try:
        for machine in machines:
            macAddress = machine.get('Mac')
            result = models.Machine.getMachineByMac(macAddress)
            if result:
                macAddesses.append(result.macAddress)
            else:
                machineName = machine.get("MachineName", '')
                machineType = machine.get("MachineType", 0)
                machineMoney= machine.get("MachineMoney", 0)
                adminPass   = machine.get("AdminPass", '')
                userPass    = machine.get("UserPass", '')
                result = models.Machine(macAddress, 
                                        machineName, 
                                        machineType  = machineType, 
                                        machineMoney = machineMoney, 
                                        adminPass    = adminPass, 
                                        userPass     = userPass)
                db.session.add(result)
                db.session.flush()
                macAddesses.append(result.macAddress)
        map(lambda address : db.session.merge(models.QuanXian(user.userName, address)), macAddesses)
        db.session.commit()
        
        return  jsonify({'Status' :  'Success', 'StatusCode':0, 'Msg' : '操作成功!'})
    except Exception, error:
        return jsonify({'Status': 'Failed', 'StatusCode':-2, 'Msg': error.message}), 400


