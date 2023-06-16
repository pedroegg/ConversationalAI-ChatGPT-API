import eventlet
eventlet.monkey_patch()

import flask
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

from api.routes.router import api

app = Flask(__name__)

app.register_blueprint(api)
app.templates_auto_reload = True

socketio = SocketIO(app)
