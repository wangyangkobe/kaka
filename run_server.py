# -*- coding: utf-8 -*-
from kaka import app
import logging
from logging.handlers import RotatingFileHandler
from flask import send_file
import os

@app.route('/log')
def log():
    return send_file("D:\\kaka\\log.txt")
        
if __name__ == '__main__':
    context = ('D:\\1889039d.private_public\\1889039d.public.pem', 'D:\\1889039d.private_public\\1889039d.private.pem')
    #context = ('/home/ubuntu/nginx.crt', '/home/ubuntu/nginx.key')
    #app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=True, threaded=True)
    
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('log.txt', maxBytes=10000000, backupCount=10)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    
    app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=False, threaded=False)
