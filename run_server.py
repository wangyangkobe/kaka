# -*- coding: utf-8 -*-
from kaka import app
if __name__ == '__main__':
    context = ('C:\\Users\\elqstux\\workspace\\elqstux.public.pem', 'C:\\Users\\elqstux\\workspace\\elqstux.private.pem')
    app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=True, threaded=True)