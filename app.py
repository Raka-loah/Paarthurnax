from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import json
import requests
import wfstate as wf

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
			resp = {
				'reply': '',
				'at_sender': 'false'
			}

			suffix = '\n更多命令请输入"帮助"。'
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
			if resp['reply'] != '':
				return resp, 200
			else:
				return '', 204
		except:
			return '', 204

# Usage:
# POST message to /
api.add_resource(wfst, '/')

# Cron jobs
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