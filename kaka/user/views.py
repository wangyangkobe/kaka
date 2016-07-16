# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from kaka import models
from kaka import db
from kaka.decorators import verify_request_json, verify_request_token
from webargs import fields
from webargs.flaskparser import use_args

user_blueprint = Blueprint('user', __name__)
