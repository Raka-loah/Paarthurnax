# -*- coding: utf-8 -*-

import importlib
import logging
import requests
from flask import Flask, jsonify, request

from Paarthurnax.core import Talking_Dragon

app = Flask(__name__)

dragon = Talking_Dragon()

@app.route('/', methods=['POST'])
def post():
    try:
        # POSTed data as json
        j = request.get_json(force=True)

        nickname = j['sender'].get('card', j['sender'].get('nickname', '')) if 'sender' in j else '#NAME?'

        app.logger.setLevel(logging.INFO)
        app.logger.info(f"[{j.get('message_type', 'UNKNOWN').upper()}][{j.get('group_id','--')}][{nickname}({j['sender'].get('user_id', '')})]:{j['message']}")

        message, status_code = dragon.hear(j)

        return jsonify(message) if message != '' else '', status_code
    except Exception as e:
        app.logger.error(f"[Exception]:{e}")
        return '', 204

@app.route('/', methods=['PATCH'])
def patch():
    try:
        try:
            request_token = request.get_json(force=True)['token']
        except:
            request_token = ''
        dragon.reload(request_token)
    except Exception as e:
        app.logger.error(f"[Exception]:{e}")
        return '', 500

if __name__ == '__main__':  
    app.run(debug=False, port=8888)
