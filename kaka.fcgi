#!/usr/bin/python

from flup.server.fcgi import WSGIServer
from kaka import app
import os

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/var/www/demoapp/kaka.sock').run()
