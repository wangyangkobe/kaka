# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/addMachines', methods=['POST'])
@verify_request_json
@verify_request_token
def addMachines():
    userName = request.json.get("User", '')
    machines = request.json.get("Machines", [])
    try:
        for machine in machines:
            macAddress  = machine.get('mac', '')
            machineName = machine.get("MachineName", '')
            if not models.Machine.getMachineByMac(macAddress):
                db.session.add(models.Machine(macAddress, machineName))
            db.session.commit()
            user = models.User.getUserByUserName(userName)
        return jsonify(request.json.get('Machines'))
    except Exception, error:
        return jsonify({'Status': 'Failed', 'StatusCode':-2, 'Msg': error.message}), 400
