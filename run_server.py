# -*- coding: utf-8 -*-
from kaka import app
from flask import request

@app.route('/')
def index():
    return 'Welocome to site: {}'.format(request.url_root)
      
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
