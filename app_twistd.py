import importlib
import json
import logging
import os
import re
import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from twisted.internet import reactor
from twisted.logger import Logger
from twisted.python import rebuild

import internal
import misc
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

C = internal.const

# Command Template:
# 'keyword': [function, fliter_type, [group_ids], cool_down, message, is_regex, is_suppressed]
#
# Parameters:
# function: Callback function
# filter_type: 0 - Blacklist, only specific groups banned from this keyword
#              1 - Whitelist, only specific groups can use this keyword, duh.
# [group_ids]: Group ids for the filter
# cool_down: Cool down of this keyword in seconds, shared between all groups
# message: True - Callback function will get POSTed message as argument
#          False - Just call that function maybe
# is_regex: True - This keyword is a regular expression
#           False - This keyword is NOT a regular expression
# is_suppressed: True - Do not append suffix or @sender tag
#                False - Append suffix or @sender tag

bot_command = {
    '警报': [wf.get_alerts, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '平原时间': [wf.get_plains_time, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '每日特惠': [wf.get_dailydeal, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '裂缝': [wf.get_fissures, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '入侵': [wf.get_invasions, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '突击': [wf.get_sorties, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '奸商': [wf.get_voidtrader, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '虚空商人': [wf.get_voidtrader, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '帮助': [wf.get_some_help, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '地球赏金': [wf.get_bounties_cetus, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '金星赏金': [wf.get_bounties_solaris, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '吃什么': [misc.general, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '早饭吃什么': [misc.breakfast, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '午饭吃什么': [misc.lunch, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '晚饭吃什么': [misc.dinner, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '小小黑': [wf.get_acolytes, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '模拟开卡': [wf.get_riven_info, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/wm': [wf.get_wmprice, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/mod': [wf.get_wiki_text, C.BLACKLIST, [], 5, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/ask': [misc.ask_8ball, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/roll': [misc.misc_roll, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/echo': [misc.msg_ar_wrapper, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/stalk': [misc.msg_ar_wrapper, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/百度': [misc.let_me_baidu_that_for_you, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '点歌': [misc.music_share, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '来首': [misc.music_share, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/tarot': [misc.draw_tarot, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wiki来': [wf.get_wiki_link, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/翻译': [misc.msg_translate_bing, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'hurt me': [misc.msg_demotivational, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'tease me': [misc.msg_tackypickuplines, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/rr': [misc.russian_roulette, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    # '/stella': [misc.msg_stella, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    r'.*今天.+了吗': [misc.msg_bankrupt, C.BLACKLIST, [], 0, C.MSG, C.REGEX, C.NOT_SUPPRESSED],
}

# Cooldown stats
stats = {}


class wfst(Resource):
    def post(self):
        try:
            # POSTed data as json
            j = request.get_json(force=True)

            # Response payload
            resp = {
                'reply': '',
                'at_sender': False
            }

            suffix = '\n更多命令请输入"帮助"。'

            # QQ Requests
            if j['post_type'] == 'request':
                if (j['request_type'] == 'group' and j['sub_type']
                        == 'invite') or j['request_type'] == 'friend':
                    resp = {
                        'approve': True
                    }
                    return resp, 200

            # Logs
            if j['post_type'] == 'message':
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

            # All queries from banned senders are directly dropped
            banned_sender = ['']
            if j['sender']['user_id'] == j['self_id'] or str(
                    j['sender']['user_id']) in banned_sender:
                return '', 204

            # CQ tag for @sender if message type is group
            at_sender = '[CQ:at,qq={}]：\n'.format(
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
                        return resp, 200
                    else:
                        stats[matched_keyword] = time.time()
                else:
                    stats[matched_keyword] = time.time()

                # Handle command
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
                    return resp, 200

            # Custom replies
            if j['message'].lower().replace(' ', '') in wf.data_dict['CR']:
                resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ', '')]
                return resp, 200

            # Autoban
            try:
                if j['message_type'] == 'group':
                    ban_word = []
                    for word in ban_word:
                        if word in j['message'].replace(' ', ''):
                            resp['ban'] = True
                            resp['ban_duration'] = 300
                            return resp, 200
            except BaseException:
                pass

            # "Execute" person nobody cared about within 120 seconds
            # The Nature of Humanity, will override Execution
            if j['message_type'] == 'group':
                resp['reply'] = misc.msg_executioner(j) if misc.msg_executioner(
                    j) != '' else misc.msg_nature_of_humanity(j)

            if resp['reply'] != '':
                return resp, 200
            else:
                return '', 204

        except Exception as e:
            log.error(repr(e))
            return '', 204

    def patch(self):
        try:
            access_token = ''  # Access Token
            try:
                request_token = request.get_json(force=True)['token']
            except BaseException:
                request_token = ''
            if request_token == access_token:
                rebuild.rebuild(wf)
                rebuild.rebuild(misc)
                return 'Successfully reloaded modules.', 200
            else:
                return 'Access Denied.', 403
        except Exception as e:
            return repr(e), 500


api.add_resource(wfst, '/')

# Cron jobs
# Change group_id to your desire group id
broadcast_group = [697991343]


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


scheduler = BackgroundScheduler()
scheduler.add_job(task_new_alert, 'cron', second='00')
scheduler.add_job(task_cetus_transition, 'cron', second='05')
scheduler.add_job(task_new_acolyte, 'cron', second='05')
scheduler.start()
