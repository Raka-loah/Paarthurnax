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

with open(os.path.dirname(os.path.abspath(__file__)) + '\\customReplies.json', 'r', encoding='utf-8') as E:
	R = json.loads(E.read())

stats = {}
stats['last_sent'] = 0
stats['last_wm_query'] = 0
stats['last_wiki_query'] = 0

app = Flask(__name__)
api = Api(app)

class wfst(Resource):
	def post(self):
		try:
			j = request.get_json(force=True)
			# Response payload
			resp = {
				'reply': '',
				'at_sender': 'false'
			}

			suffix = '\n更多命令请输入"帮助"。'

			if j['post_type'] == 'request' and j['request_type'] == 'group':
				resp = {
					'approve': 'true'
				}
				return resp, 200
			
			if j['post_type'] == 'message':
				if j['message_type'] == 'group':
					misc.msg_log(j['message_id'], j['group_id'], j['sender']['user_id'], j['message'])
				else:
					misc.msg_log(j['message_id'], '0', j['sender']['user_id'], j['message'])

			# All queries from banned senders are directly dropped
			banned_sender = ['']
			if j['sender']['user_id'] == j['self_id'] or str(j['sender']['user_id']) in banned_sender:
				return '', 204

			if j['message'] == '警报':
				resp['reply'] = wf.get_alerts() + suffix
			elif j['message'] == '平原时间':
				resp['reply'] = wf.get_cetus_time() + '\n' + wf.get_fortuna_time() + suffix
			elif j['message'] == '突击':
				resp['reply'] = wf.get_sorties() + suffix
			elif j['message'] == '地球赏金':
				resp['reply'] = wf.get_bounties('cetus') + suffix
			elif j['message'] == '金星赏金':
				resp['reply'] = wf.get_bounties('solaris') + suffix
			elif j['message'] == '裂缝':
				resp['reply'] = wf.get_fissures() + suffix        
			elif j['message'] == '入侵':
				resp['reply'] = wf.get_invasions() + suffix  
			elif j['message'].startswith('模拟开卡'):
				if time.time() - stats['last_sent'] > 60:
					if 'card' in j['sender'] and j['sender']['card'] != '':
						resp['reply'] = '[' + j['sender']['card'] + ']' + wf.get_riven_info(j['message'].replace('模拟开卡', '').strip())
						stats['last_sent'] = time.time()
					elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
						resp['reply'] = '[' + j['sender']['nickname'] + ']' + wf.get_riven_info(j['message'].replace('模拟开卡', '').strip())
						stats['last_sent'] = time.time()
					else:
						resp['reply'] = wf.get_riven_info(j['message'].replace('模拟开卡', '').strip())
						stats['last_sent'] = time.time()
				else:
					if 'card' in j['sender'] and j['sender']['card'] != '':
						resp['reply'] = '[' + j['sender']['card'] + ']\n' + wf.cooldown()
					elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
						resp['reply'] = '[' + j['sender']['nickname'] + ']\n' + wf.cooldown()
					else:
						resp['reply'] = wf.cooldown()																		
			elif j['message'] == '帮助':
				resp['reply'] = '目前可用命令：\n帮助、警报、入侵、平原时间、地球赏金、金星赏金、突击、裂缝'
			elif j['message'].lower().replace(' ','') in R:
				resp['reply'] = R[j['message'].lower().replace(' ','')]
			elif j['message'].startswith('/roll'):
				msg = wf.misc_roll(j['message'])
				if msg != '':
					if j['message_type'] == 'group':
						if 'card' in j['sender'] and j['sender']['card'] != '':
							resp['reply'] = '[' + j['sender']['card'] + ']' + msg
						elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
							resp['reply'] = '[' + j['sender']['nickname'] + ']' + msg
						else:
							resp['reply'] = msg
					else:
						resp['reply'] = msg
			elif j['message'].startswith('/ask'):
				resp['reply'] = wf.ask_8ball(j['message'])
			elif j['message'].startswith('/wm'):
				if time.time() - stats['last_wm_query'] > 10:		
					msg = wf.get_wmprice(j['message'].replace('/wm', '').strip())
					stats['last_wm_query'] = time.time()
				else:
					msg = wf.cooldown()
				if msg != '':
					if j['message_type'] == 'group':
						if 'card' in j['sender'] and j['sender']['card'] != '':
							resp['reply'] = '[' + j['sender']['card'] + ']\n' + msg
						elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
							resp['reply'] = '[' + j['sender']['nickname'] + ']\n' + msg
						else:
							resp['reply'] = msg
					else:
						resp['reply'] = msg
			elif j['message'].startswith('/mod'):
				if time.time() - stats['last_wiki_query'] > 10:
					msg = wf.get_wiki_text(j['message'].replace('/mod', '').strip())
					stats['last_wiki_query'] = time.time()
				else:
					msg = wf.cooldown()
				if msg != '':
					if j['message_type'] == 'group':
						if 'card' in j['sender'] and j['sender']['card'] != '':
							resp['reply'] = '[' + j['sender']['card'] + ']\n' + msg
						elif 'nickname' in j['sender'] and j['sender']['nickname'] != '':
							resp['reply'] = '[' + j['sender']['nickname'] + ']\n' + msg
						else:
							resp['reply'] = msg
					else:
						resp['reply'] = msg
			#TODO: Dictionary these
			elif j['message'].startswith('早饭吃什么'):
				msg = ''
				for dish in misc.food('breakfast'):
					msg += dish + ' '
				resp['reply'] = msg
			elif j['message'].startswith('午饭吃什么'):
				msg = ''
				for dish in misc.food('lunch'):
					msg += dish + ' '
				resp['reply'] = msg
			elif j['message'].startswith('晚饭吃什么'):
				msg = ''
				for dish in misc.food('dinner'):
					msg += dish + ' '
				resp['reply'] = msg
			elif j['message'] == ('吃什么'):
				msg = ''
				for dish in misc.food(''):
					msg += dish + ' '
				resp['reply'] = msg
			elif j['message'].startswith('/echo'):
				query_id = re.match(r'.*\[CQ:at,qq=(.*)\].*', j['message'])
				if query_id and j['message_type'] == 'group':
					resp['reply'] = misc.msg_fetch(j['group_id'], query_id.group(1))

			if j['message_type'] == 'group':
				autoban(j['message'], j['group_id'], j['user_id'])

			if resp['reply'] != '':
				return resp, 200
			else:
				return '', 204
		except:
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