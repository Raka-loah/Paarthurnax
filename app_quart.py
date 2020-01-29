# -*- coding: utf-8 -*-

import importlib
import logging

from quart import Quart, jsonify, request

from message_handler import Message_handler

from logging.config import dictConfig

import wfstate as wf

dictConfig({
    'version': 1,
    'loggers': {
        'quart.app': {
            'level': 'INFO',
        },
    },
})

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    handlers=[
        logging.FileHandler(
            'qqbot.log',
            'a',
            'utf-8')])

app = Quart(__name__)

handler = Message_handler()

@app.route('/', methods=['POST'])
async def post():
    try:
        # POSTed data as json
        j = await request.get_json(force=True)
        
        if j['message_type'] == 'group':
            if 'card' in j['sender'] and j['sender']['card'] != '':
                app.logger.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['card'], j['sender']['user_id'], j['message']))
            elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
                app.logger.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['nickname'], j['sender']['user_id'], j['message']))
            else:
                app.logger.info('[%s][%s]:%s' % (j['group_id'], j['sender']['user_id'], j['message']))
        else:
            app.logger.info('[%s]:%s' % (j['sender']['user_id'], j['message']))

        message, status_code = handler.handle(j)

        return jsonify(message), status_code

    except Exception as e:
        print(e)
        return '', 204

@app.route('/', methods=['PATCH'])
async def patch():
    try:
        try:
            request_token = await request.get_json(force=True)['token']
        except BaseException:
            request_token = ''
        handler.reload(request_token)
    except Exception as e:
        return print(e), 500

handler.add_job(wf.get_new_alerts, second='00')
handler.add_job(wf.get_cetus_transition, second='05')
handler.add_job(wf.get_new_acolyte, second='00')

if __name__ == '__main__':
    app.run(debug=False, port=8888)