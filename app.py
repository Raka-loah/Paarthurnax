from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import json
import requests
import wfstate as wf
import misc
import re

app = Flask(__name__)
api = Api(app)

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
	'吃什么': misc.general,
	'早饭吃什么': misc.breakfast,
	'午饭吃什么': misc.lunch,
	'晚饭吃什么': misc.dinner
}

# Commands that need arguments and will get POSTed json as argument
command_partial = {
	'地球赏金': wf.get_bounties,
	'金星赏金': wf.get_bounties,
	'模拟开卡': wf.get_riven_info,
	'/wm': wf.get_wmprice,
	'/mod': wf.get_wiki_text,
	'/ask': wf.ask_8ball,
	'/roll': wf.misc_roll,
	'/echo': misc.msg_ar_wrapper,
	'/stalker': misc.msg_ar_wrapper
}

# Do not append suffix or @sender tag
command_suppress = ['吃什么', '早饭吃什么', '午饭吃什么', '晚饭吃什么']

# Cooldown for individual commands in seconds
command_cooldown_full = {}

command_cooldown_partial = {
	'模拟开卡': 10,
	'/wm': 10,
	'/mod': 5
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
				'at_sender': 'false'
			}

			suffix = '\n更多命令请输入"帮助"。'

			# QQ Requests
			if j['post_type'] == 'request':
				if j['request_type'] == 'group':
					resp = {
						'approve': 'true'
					}
					return resp, 200
			
			# Logs
			log_msg = True
			if log_msg and j['post_type'] == 'message':
				if j['message_type'] == 'group':
					misc.msg_log(j['message_id'], j['group_id'], j['sender']['user_id'], j['message'])
				else:
					misc.msg_log(j['message_id'], '0', j['sender']['user_id'], j['message'])

			# All queries from banned senders and bot themselves are directly dropped
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

			# Handle commands
			for command in command_full:
				if j['message'] == command:
					msg = command_full.get(command, lambda: '')()
					if msg != '':
						if command in command_suppress:
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

			# Custom replies
			if j['message'].lower().replace(' ','') in wf.data_dict['CR']:
				resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ','')]
				return resp, 200

			# Autoban
			if j['message_type'] == 'group':
				autoban(j['message'], j['group_id'], j['user_id'])
			
			# This is basically not possible due to every message being handled above, but what if something weird happened?
			if resp['reply'] != '':
				return resp, 200
			else:
				return '', 204

		except Exception as e:
			print(repr(e))
			return '', 204

def autoban(message, group_id, user_id):
	ban_word = ['惊闻', '文体两开花']
	for word in ban_word:
		if word in message.replace(' ',''):
			url = 'http://127.0.0.1:5700/set_group_ban'
			payload = {
				'group_id': group_id,
				'user_id': user_id,
				'duration': 300
			}
			requests.post(url, json=payload)
			break

# Usage:
# POST message to /
api.add_resource(wfst, '/')

# Cron jobs
# Change group_id to your desire group id
def task_new_alert():
	msg = wf.get_new_alerts()
	if msg != '':
		url = 'http://127.0.0.1:5700/send_group_msg_async'
		payload = {
			'group_id': 697991343,
			'message': msg
		}
		requests.post(url, json=payload)

def task_cetus_transition():
	msg = wf.get_cetus_transition()
	if msg != '':
		url = 'http://127.0.0.1:5700/send_group_msg_async'
		payload = {
			'group_id': 697991343,
			'message': msg
		}
		requests.post(url, json=payload)

if __name__ == '__main__':
	scheduler = BackgroundScheduler()
	scheduler.add_job(task_new_alert, 'cron', second='00')
	scheduler.add_job(task_cetus_transition, 'cron', second='05')
	scheduler.start()
	app.run(debug=False,port=8888)