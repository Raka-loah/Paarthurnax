# -*- coding: utf-8 -*-

import importlib
import logging

from quart import Quart, jsonify, request, render_template
from Paarthurnax.core import Talking_Dragon

app = Quart(__name__, static_url_path='', static_folder='Paarthurnax/admin', template_folder='Paarthurnax/admin')

dragon = Talking_Dragon()

@app.route('/', methods=['POST'])
async def post():
    try:
        # POSTed data as json
        j = await request.get_json(force=True)

        nickname = j['sender'].get('card', j['sender'].get('nickname', '')) if 'sender' in j else '#NAME?'
        
        app.logger.setLevel(logging.INFO)
        app.logger.info(f"[{j.get('message_type', 'UNKNOWN').upper()}][{j.get('group_id','--')}][{nickname}({j['sender'].get('user_id', '')})]:{j['message']}")

        message, status_code = dragon.hear(j)

        return jsonify(message) if message != '' else '', status_code

    except Exception as e:
        app.logger.error(f"[Exception]:{e}")
        return '', 204

@app.route('/admin/settings', methods=['GET', 'POST'])
async def admin_settings():
    if request.method == 'GET':
        return jsonify(dragon.tell()), 200
    elif request.method == 'POST':
        return dragon.take(request.get_json(force=True))
    return '', 204

@app.route('/admin', methods=['GET'])
async def admin():
    return render_template('index.htm')

if __name__ == '__main__':
    app.run(debug=False, port=8888)