# -*- coding: utf-8 -*-

import importlib
import logging
import requests
from flask import Flask, jsonify, request

from message_handler import Message_handler

import wfstate as wf

app = Flask(__name__)

handler = Message_handler()

@app.route('/', methods=['POST'])
def post():
    try:
        # POSTed data as json
        j = request.get_json(force=True)

        nickname = j['sender'].get('card', j['sender'].get('nickname', '')) if 'sender' in j else '#NAME?'

        app.logger.setLevel(logging.INFO)
        app.logger.info(f"[{j.get('message_type', 'UNKNOWN').upper()}][{j.get('group_id','--')}][{nickname}({j['sender'].get('user_id', '')})]:{j['message']}")

        message, status_code = handler.handle(j)

        return jsonify(message), status_code
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
        handler.reload(request_token)
    except Exception as e:
        app.logger.error(f"[Exception]:{e}")
        return '', 500

if __name__ == '__main__':  
    handler.add_job(wf.get_new_alerts, second='00')
    handler.add_job(wf.get_cetus_transition, second='05')
    handler.add_job(wf.get_new_acolyte, second='00')
    app.run(debug=False, port=8888)
