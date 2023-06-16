import flask
from flask import Blueprint, request, render_template

import json
import logging

import api.handlers.handler as handler
from library.errors import BaseError, InternalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

api = Blueprint('api', __name__, url_prefix='/api/')

@api.route('/chat-topics', methods=['GET'])
def GetTopics():
    return handler.GetTopics()

@api.route('/new-chat', methods=['POST'])
def StartNewChat():
    return handler.NewChat()

@api.route('/process-message', methods=['POST'])
def ProcessMessage():
    return handler.ProcessMessage()

@api.route('/translate', methods=['POST'])
def Translate():
    return handler.Translate()

@api.errorhandler(BaseError)
def handle_crafted_errors(e: BaseError):
    response = e.get_response()
    response.data = json.dumps({
        'error': {
            'code': e.code,
            'name': e.name,
            'description': e.description,
        },
    })
    response.content_type = 'application/json'
    response.charset = 'utf-8'

    return response

@api.errorhandler(Exception)
def handle_exception(e: Exception):
    logger.error(e, exc_info=1)
    return handle_crafted_errors(InternalError(e.__str__()))
