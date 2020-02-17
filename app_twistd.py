# -*- coding: utf-8 -*-

import importlib
import logging

from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from twisted.internet import reactor
from twisted.logger import Logger
from twisted.python import rebuild

from message_handler import Message_handler

import wfstate as wf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    handlers=[
        logging.FileHandler(
            'qqbot.log',
            'a',
            'utf-8')])

app = Flask(__name__)
api = Api(app)

log = Logger()

handler = Message_handler()

class wfst(Resource):
    def post(self):
        try:
            # POSTed data as json
            j = request.get_json(force=True)

            if j['message_type'] == 'group':
                if 'card' in j['sender'] and j['sender']['card'] != '':
                    log.info(
                        '[%s][%s(%s)]:%s' %
                        (j['group_id'],
                         j['sender']['card'],
                            j['sender']['user_id'],
                            j['message']))
                    logging.info(
                        '[%s][%s(%s)]:%s' %
                        (j['group_id'],
                         j['sender']['card'],
                            j['sender']['user_id'],
                            j['message']))
                elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
                    log.info(
                        '[%s][%s(%s)]:%s' %
                        (j['group_id'],
                         j['sender']['nickname'],
                            j['sender']['user_id'],
                            j['message']))
                    logging.info(
                        '[%s][%s(%s)]:%s' %
                        (j['group_id'],
                         j['sender']['nickname'],
                            j['sender']['user_id'],
                            j['message']))
                else:
                    log.info(
                        '[%s][%s]:%s' %
                        (j['group_id'],
                         j['sender']['user_id'],
                            j['message']))
                    logging.info(
                        '[%s][%s]:%s' %
                        (j['group_id'], j['sender']['user_id'], j['message']))
            else:
                log.info('[%s]:%s' % (j['sender']['user_id'], j['message']))
                logging.info('[%s]:%s' %
                             (j['sender']['user_id'], j['message']))

            return handler.handle(j)

        except Exception as e:
            log.error(repr(e))
            return '', 204

    def patch(self):
        try:
            try:
                request_token = request.get_json(force=True)['token']
            except BaseException:
                request_token = ''
            handler.reload(request_token)
        except Exception as e:
            return print(e), 500


api.add_resource(wfst, '/')

handler.add_job(wf.get_new_alerts, second='00')
handler.add_job(wf.get_cetus_transition, second='05')
handler.add_job(wf.get_new_acolyte, second='00')
