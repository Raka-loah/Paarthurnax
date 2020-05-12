# -*- coding: utf-8 -*-

import importlib
import logging

from flask import Flask, jsonify, request
from twisted.internet import reactor
from twisted.logger import Logger
from twisted.python import rebuild

from message_handler import Message_handler

import wfstate as wf

app = Flask(__name__)

log = Logger()

handler = Message_handler()

@app.route('/', methods=['POST'])
def post():
    try:
        # POSTed data as json
        j = request.get_json(force=True)

        nickname = j['sender'].get('card', j['sender'].get('nickname', '')) if 'sender' in j else '#NAME?'

        log.info(f"[{j.get('message_type', 'UNKNOWN').upper()}][{j.get('group_id','--')}][{nickname}({j['sender']['user_id']})]:{j['message']}")

        return handler.handle(j)

    except Exception as e:
        log.error(e)
        return '', 204

@app.route('/', methods=['PATCH'])
def patch():
    try:
        try:
            request_token = request.get_json(force=True)['token']
        except BaseException:
            request_token = ''
        handler.reload(request_token)
    except Exception as e:
        log.error(e)
        return '', 500


handler.add_job(wf.get_new_alerts, second='00')
handler.add_job(wf.get_cetus_transition, second='05')
handler.add_job(wf.get_new_acolyte, second='00')
