# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@localhost/kaka_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret string'
db = SQLAlchemy(app)


from kaka.api.views import api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')