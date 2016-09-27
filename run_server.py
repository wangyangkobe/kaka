# -*- coding: utf-8 -*-
from kaka import app
from flask import request

@app.route('/')
def index():
    if request.url_root.find("5000") != -1:
        return '亲爱的，欢迎来到正式版!'
    else:
        return '亲爱的，欢迎来到开发版!'
      
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=False)
