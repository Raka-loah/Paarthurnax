from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from twisted.internet import reactor
from twisted.logger import Logger
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import json
import requests
import wfstate as wf
import misc
import re	
import logging
logging.basicConfig(level=logging.INFO,
					format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
					datefmt='%m-%d %H:%M',
					handlers=[logging.FileHandler('qqbot.log', 'a', 'utf-8')])

app = Flask(__name__)
api = Api(app)

log = Logger()

# Commands that need a full match on keyword and take no arguments at all
command_full = {
	'警报': wf.get_alerts,
	'平原时间': wf.get_plains_time,
	'每日特惠': wf.get_dailydeal,
	'裂缝': wf.get_fissures,
	'入侵': wf.get_invasions,
	'突击': wf.get_sorties,
	'奸商': wf.get_voidtrader,
	'虚空商人': wf.get_voidtrader,
	'帮助': wf.get_some_help,
	'地球赏金': wf.get_bounties_cetus,
	'金星赏金': wf.get_bounties_solaris,
	'吃什么': misc.general,
	'早饭吃什么': misc.breakfast,
	'午饭吃什么': misc.lunch,
	'晚饭吃什么': misc.dinner,
	'小小黑': wf.get_acolytes
}

# Commands that need arguments and will get POSTed json as argument
command_partial = {
	'模拟开卡': wf.get_riven_info,
	'/wm': wf.get_wmprice,
	'/mod': wf.get_wiki_text,
	'/ask': wf.ask_8ball,
	'/roll': wf.misc_roll,
	'/echo': misc.msg_ar_wrapper,
	'/stalk': misc.msg_ar_wrapper,
	'/百度': misc.let_me_baidu_that_for_you,
	'点歌': misc.music_share,
	'来首': misc.music_share,
	'/tarot': misc.draw_tarot,
	'wiki来': wf.get_wiki_link,
	'/翻译': misc.msg_translate_bing,
	'hurt me': misc.msg_demotivational,
	'tease me': misc.msg_tackypickuplines,
	'/rr': misc.russian_roulette
}

# Do not append suffix or @sender tag
command_suppress = ['帮助', '吃什么', '早饭吃什么', '午饭吃什么', '晚饭吃什么', '/百度', '点歌', '来首', 'wiki来']

# Cooldown for individual command in seconds
command_cooldown_full = {}

command_cooldown_partial = {
	'模拟开卡': 10,
	'/wm': 10,
	'/mod': 5,
	'/百度': 10,
	'/tarot': 10,
	'wiki来': 10,
	'/翻译': 10
}

command_cooldown_advanced = {}

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
				if (j['request_type'] == 'group' and j['sub_type'] == 'invite') or j['request_type'] == 'friend':
					resp = {
						'approve': True
					}
					return resp, 200
			
			# Logs
			if j['post_type'] == 'message':
				if j['message_type'] == 'group':
					misc.msg_log(j['message_id'], j['group_id'], j['sender']['user_id'], j['message'])
				else:
					misc.msg_log(j['message_id'], '0', j['sender']['user_id'], j['message'])

			if j['message_type'] == 'group':
				if 'card' in j['sender'] and j['sender']['card'] != '':
					log.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['card'], j['sender']['user_id'], j['message']))
					logging.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['card'], j['sender']['user_id'], j['message']))
				elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
					log.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['nickname'], j['sender']['user_id'], j['message']))
					logging.info('[%s][%s(%s)]:%s' % (j['group_id'], j['sender']['nickname'], j['sender']['user_id'], j['message']))
				else:
					log.info('[%s][%s]:%s' % (j['group_id'], j['sender']['user_id'], j['message']))
					logging.info('[%s][%s]:%s' % (j['group_id'], j['sender']['user_id'], j['message']))
			else:
				log.info('[%s]:%s' % (j['sender']['user_id'], j['message']))
				logging.info('[%s]:%s' % (j['sender']['user_id'], j['message']))

			# All queries from banned senders are directly dropped
			banned_sender = ['']
			if j['sender']['user_id'] == j['self_id'] or str(j['sender']['user_id']) in banned_sender:
				return '', 204

			# CQ tag for @sender if message type is group
			at_sender = '[CQ:at,qq={}]：\n'.format(j['sender']['user_id']) if j['message_type'] == 'group' else ''

			# Check query cooldown
			for cd in command_cooldown_full:
				if cd in j['message']:
					if cd in stats:
						if time.time() - stats[cd] < command_cooldown_full[cd]:
							resp['reply'] = at_sender + wf.cooldown()
							return resp, 200
						else:
							stats[cd] = time.time()
					else:
						stats[cd] = time.time()

			for cd in command_cooldown_partial:
				if j['message'].startswith(cd):
					if cd in stats:
						if time.time() - stats[cd] < command_cooldown_partial[cd]:
							resp['reply'] = at_sender + wf.cooldown()
							return resp, 200
						else:
							stats[cd] = time.time()
					else:
						stats[cd] = time.time()

			for cd in command_cooldown_advanced:
				match = re.match(cd, j['message'])
				if match:
					if cd in stats:
						if time.time() - stats[cd] < command_cooldown_advanced[cd]:
							resp['reply'] = at_sender + wf.cooldown()
							return resp, 200
						else:
							stats[cd] = time.time()
					else:
						stats[cd] = time.time()

			# Handle commands
			msg = command_full.get(j['message'], lambda: '')()
			if msg != '':
				if j['message'] in command_suppress:
					resp['reply'] = msg
				else:
					resp['reply'] = msg + suffix
				return resp, 200

			for command in command_partial:
				if j['message'].startswith(command):
					msg = command_partial.get(command, lambda: '')(j)
					if msg != '':
						if command in command_suppress:
							resp['reply'] = msg
						else:
							resp['reply'] = at_sender + msg
						return resp, 200						

			for command in command_advanced:
				match = re.match(command, j['message'])
				if match:
					msg = command_advanced.get(command, lambda: '')(j)
					if msg != '':
						if command in command_suppress:
							resp['reply'] = msg
						else:
							resp['reply'] = at_sender + msg
						return resp, 200

			# Custom replies
			if j['message'].lower().replace(' ','') in wf.data_dict['CR']:
				resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ','')]
				return resp, 200

			# Autoban
			if j['message_type'] == 'group':
				ban_word = ['惊闻', '文体两开花', '驚聞']
				for word in ban_word:
					if word in j['message'].replace(' ',''):	
						resp['ban'] = True
						resp['ban_duration'] = 300
						return resp, 200

			# "Execute" person nobody cared about within 120 seconds
			# The Nature of Humanity, will override Execution
			if j['message_type'] == 'group':
				resp['reply'] = misc.msg_executioner(j) if misc.msg_executioner(j) != '' else misc.msg_nature_of_humanity(j)

			if resp['reply'] != '':
				return resp, 200
			else:
				return '', 204

		except Exception as e:
			log.error(repr(e))
			return '', 204

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