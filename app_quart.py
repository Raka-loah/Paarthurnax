# -*- coding: utf-8 -*-

import importlib
import html
import json
import logging
import os
import re
import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from quart import Quart, jsonify, request

import internal
import misc
import trivia
import wfstate as wf

from logging.config import dictConfig

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

try:
    cfg = importlib.import_module('config')
except ImportError:
    cfg = importlib.import_module('config-sample')

C = internal.const

bot_command = cfg.bot_command

# Cooldown stats
stats = {}

@app.route('/', methods=['POST'])
async def post():
    try:
        # POSTed data as json
        j = await request.get_json(force=True)

        # Response payload
        resp = {
            'reply': '',
            'at_sender': False
        }

        suffix = cfg.suffix

        if 'message' in j:
            j['message'] = html.unescape(j['message'])

        # QQ Requests
        if j['post_type'] == 'request':
            if (j['request_type'] == 'group' and j['sub_type']
                    == 'invite') or j['request_type'] == 'friend':
                resp = {
                    'approve': cfg.approve
                }
                return jsonify(resp), 200

        # Logs
        log_msg = True
        if log_msg and j['post_type'] == 'message':
            if j['message_type'] == 'group':
                misc.msg_log(
                    j['message_id'],
                    j['group_id'],
                    j['sender']['user_id'],
                    j['message'])
            else:
                misc.msg_log(
                    j['message_id'],
                    '0',
                    j['sender']['user_id'],
                    j['message'])

        if j['message_type'] == 'group':
            if 'card' in j['sender'] and j['sender']['card'] != '':
                app.logger.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['card'], j['sender']['user_id'], j['message']))
            elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
                app.logger.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['nickname'], j['sender']['user_id'], j['message']))
            else:
                app.logger.info('[%s][%s]:%s' % (j['group_id'], j['sender']['user_id'], j['message']))
        else:
            app.logger.info('[%s]:%s' % (j['sender']['user_id'], j['message']))

        # All queries from banned senders and bot themselves are directly
        # dropped
        banned_sender = cfg.banned_sender
        if j['sender']['user_id'] == j['self_id'] or j['sender']['user_id'] in banned_sender:
            return '', 204

        # CQ tag for @sender if message type is group
        title = ''
        if hasattr(cfg, 'custom_title') and j['message_type'] == 'group':
            if j['sender']['user_id'] in cfg.custom_title:
                if j['group_id'] in cfg.custom_title[j['sender']['user_id']]:
                    title = cfg.custom_title[j['sender']['user_id']][j['group_id']]
                elif 'default' in cfg.custom_title[j['sender']['user_id']]:
                    title = cfg.custom_title[j['sender']['user_id']]['default']
            elif 'default' in cfg.custom_title:
                title = cfg.custom_title['default']

        at_sender = '{}[CQ:at,qq={}]：\n'.format(title, 
            j['sender']['user_id']) if j['message_type'] == 'group' else ''

        # Determine which keyword got called
        matched_keyword = None
        for keyword, function in bot_command.items():
            # Is it a regex?
            if function[5] == C.REGEX:
                match = re.match(keyword, j['message'])
                if match:
                    matched_keyword = keyword
                    break
            # Is it a full match?
            elif function[4] == C.NO_MSG:
                if j['message'] == keyword:
                    matched_keyword = keyword
                    break
            # Is it a partial match?
            elif j['message'].startswith(keyword):
                matched_keyword = keyword
                break
        
        # Check filter
        if matched_keyword is not None:
            if j['message_type'] == 'group':
                if bot_command[matched_keyword][1] == C.BLACKLIST:
                    if j['group_id'] in bot_command[matched_keyword][2]:
                        matched_keyword = None
                else:
                    if j['group_id'] not in bot_command[matched_keyword][2]:
                        matched_keyword = None

        # If we got a keyword
        if matched_keyword is not None:
            # Check cooldown
            if matched_keyword in stats:
                if time.time() - stats[matched_keyword] < bot_command[matched_keyword][3]:
                    resp['reply'] = at_sender + internal.cooldown()
                    return jsonify(resp), 200
                else:
                    stats[matched_keyword] = time.time()
            else:
                stats[matched_keyword] = time.time()

            # Handle command
            j['keyword'] = matched_keyword
            try:
                if bot_command[matched_keyword][4] == C.NO_MSG:
                    msg = bot_command[matched_keyword][0]()
                else:
                    msg = bot_command[matched_keyword][0](j)
            except BaseException:
                msg = ''

            if msg != '':
                # Is keyword suppressed?
                if bot_command[matched_keyword][6] == C.SUPPRESSED:
                    resp['reply'] = msg
                elif bot_command[matched_keyword][4] == C.NO_MSG:
                    resp['reply'] = msg + suffix
                else:
                    resp['reply'] = at_sender + msg
                return jsonify(resp), 200

        # Custom replies
        if j['message'].lower().replace(' ', '') in wf.data_dict['CR']:
            resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ', '')]
            return jsonify(resp), 200

        # Autoban
        try:
            if j['message_type'] == 'group':
                ban_word = cfg.ban_word
                for word in ban_word:
                    if word in j['message'].replace(' ', ''):
                        resp['ban'] = True
                        resp['ban_duration'] = cfg.ban_duration
                        return jsonify(resp), 200
        except BaseException:
            pass

        # Trivia
        try:
            if j['message_type'] == 'group':
                resp['reply'] = trivia.triviabot(j)
                if resp['reply'] != '':
                    return jsonify(resp), 200
        except BaseException:
            pass

        try:
            if j['message'].lower().strip() == trivia.curr[j['group_id']]['answer'].lower().strip():
                return '', 204
        except BaseException:
            pass

        # "Execute" person nobody cared about within 120 seconds
        # The Nature of Humanity, will override Execution
        if j['message_type'] == 'group':
            resp['reply'] = misc.msg_executioner(j) if misc.msg_executioner(
                j) != '' else misc.msg_nature_of_humanity(j)

        if resp['reply'] != '':
            return jsonify(resp), 200
        else:
            return '', 204

    except Exception as e:
        print(repr(e))
        return '', 204

@app.route('/', methods=['PATCH'])
async def patch():
    try:
        access_token = cfg.reload_token  # Access Token
        try:
            request_token = await request.get_json(force=True)['token']
        except BaseException:
            request_token = ''
        if request_token == access_token:
            importlib.reload(wf)
            importlib.reload(misc)
            return 'Successfully reloaded modules.', 200
        else:
            return 'Access Denied.', 403
    except Exception as e:
        return repr(e), 500


# Cron jobs
# Change group_id to your desire group id
broadcast_group = cfg.broadcast_group


def task_new_alert():
    msg = wf.get_new_alerts()
    if msg != '':
        url = 'http://127.0.0.1:5700/send_group_msg_async'
        for group_id in broadcast_group:
            payload = {
                'group_id': group_id,
                'message': msg
            }
            requests.post(url, json=payload)


def task_cetus_transition():
    msg = wf.get_cetus_transition()
    if msg != '':
        url = 'http://127.0.0.1:5700/send_group_msg_async'
        for group_id in broadcast_group:
            payload = {
                'group_id': group_id,
                'message': msg
            }
            requests.post(url, json=payload)


def task_new_acolyte():
    msg = wf.get_new_acolyte()
    if msg != '':
        url = 'http://127.0.0.1:5700/send_group_msg_async'
        for group_id in broadcast_group:
            payload = {
                'group_id': group_id,
                'message': msg
            }
            requests.post(url, json=payload)


if cfg.enable_broadcast:
    scheduler = BackgroundScheduler()
    scheduler.add_job(task_new_alert, 'cron', second='00')
    scheduler.add_job(task_cetus_transition, 'cron', second='05')
    scheduler.add_job(task_new_acolyte, 'cron', second='05')
    scheduler.start()