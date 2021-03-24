# -*- coding: utf-8 -*-

import importlib
import logging
import requests
from flask import Flask, jsonify, request, render_template

from Paarthurnax.core import Talking_Dragon

app = Flask(__name__, static_url_path='', static_folder='Paarthurnax/admin', template_folder='Paarthurnax/admin')

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

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if request.method == 'GET':
        return jsonify(dragon.tell()), 200
    elif request.method == 'POST':
        return dragon.take(request.get_json(force=True))
    return '', 204

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('index.htm')

@app.route('/whisper', methods=['POST'])
def whisper(): 
    try:
        # POSTed data as json
        j = request.get_json(force=True)
        app.logger.info(j)

        message, status_code = dragon.hear(j)
        app.logger.info(message)
        app.logger.info(status_code)
        return jsonify(message) if message != '' else '', status_code
    except Exception as e:
        app.logger.error(f"[Exception]:{e}")
        return '', 204

if __name__ == '__main__':  
    app.run(debug=True, port=8888)
