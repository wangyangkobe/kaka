# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args
from webargs.core import ValidationError

admin_blueprint = Blueprint('admin', __name__)

def checkUserNameExist(userName):
    if models.User.getUserByUserName(userName):
        return True
    else:
        raise ValidationError("The user \"{}\" don't exist!".format(userName))
    
@admin_blueprint.route('/addMachines', methods=['POST'])
@verify_request_json
@use_args({'User'     : fields.Str(required=True, validate=checkUserNameExist),
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
    print machines
    user = models.User.getUserByUserName(userName)
    try:
        for machine in machines:
            print machine
            macAddress  = machine.get('mac', '')
            machineName = machine.get("MachineName", '')
            machineType = machine.get("MachineType", 0)
            machineMoney= machine.get("MachineMoney", 0)
            adminPass   = machine.get("adminPass", '')
            userPass    = machine.get("UserPass", '')
            machine = models.Machine(macAddress, machineName, machineType=machineType, 
                                     machineMoney=machineMoney, adminPass=adminPass, userPass=userPass)
            #db.session.add(machine)
            user.machines.append(machine)
        db.session.add(user)
        db.session.commit()
        
        return jsonify(request.json.get('Machines'))
    except Exception, error:
        return jsonify({'Status': 'Failed', 'StatusCode':-2, 'Msg': error.message}), 400
