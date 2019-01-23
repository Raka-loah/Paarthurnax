import random

def food(meal):
	dishlist = {
		'general': ['炒饭', '炒面', '泡面', '煮面', '匹萨', '烧麦', '拉肠', '炒牛河', '海带', '炸鸡', '关东煮', '米线', '面包'],
		'breakfast': ['油条', '糯米鸡', '馅饼', '肉包子', '煎堆', '素包子', '糊辣汤', '肉粥', '甜粥', '馒头', '饭团', '昨晚的剩饭', '锅贴', '生煎', '冷面', '馄饨', '小笼', '煎饼果子', '大饼夹一切', '豆汁', '焦圈', '卤煮', '炒肝', '肉夹馍', '鸡蛋灌饼'],
		'lunch': ['宫保鸡丁', '红烧肉', '扬州狮子头', '腌笃鲜', '冒菜', '缅甸菜', '赛百味', '麦当劳', '肯德基', '汉堡王', '德克士', '华莱士', '鱼香肉丝', '西红柿炒鸡蛋', '排骨饭', '麻辣香锅', '水煮鱼', '卤肉饭', '鸡排饭', '沙拉', '黄焖鸡', '酸菜鱼'],
		'dinner': ['馒头', '火锅', '傣族菜', '漆油鸡', '柠檬撒', '汉堡包', '寿喜烧', '方便面', '意大利面', '通心粉', '拉面', '盖饭', '麻辣香锅', '麻辣烫', '麻辣拌', '鸭血粉丝', '鸡公煲', '糖醋里脊', '糖醋排骨', '熏鱼']
	}
	dishes = dishlist['general']
	if meal in dishlist:
		for dish in dishlist[meal]:
			dishes.append(dish)

	selected_dishes = []
	for _ in range(0,3):
		selected_dish = random.choice(dishes)
		selected_dishes.append(selected_dish)
		dishes.remove(selected_dish)

	msg = ''
	for dish in selected_dishes:
		msg += dish + ' '

	return msg

def breakfast():
	return food('breakfast')

def lunch():
	return food('lunch')

def dinner():
	return food('dinner')

def general():
	return food('')

def wikilink():
	return 'Warframe Wiki : https://warframe.huijiwiki.com/wiki/%E9%A6%96%E9%A1%B5'
import sqlite3
import time

def msg_log(message_id, group_id, sender_id, message):
	try:
		db = sqlite3.connect('qqbot.sqlite')
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, group_id INTEGER, sender_id INTEGER, message TEXT, timestamp REAL)''')
		db.commit()
	except:
		db.rollback()
		db.close()
		return '[ERROR] Database error'
	
	try:
		cursor.execute('''INSERT INTO messages(id, group_id, sender_id, message, timestamp) VALUES(?, ?, ?, ?, ?)''', (message_id, group_id, sender_id, message, time.time()))
		db.commit()
	except:
		db.rollback()
	finally:
		db.close()
		return '[INFO] Transaction complete'

def msg_fetch(group_id, sender_id, lines=5):
	try:
		db = sqlite3.connect('qqbot.sqlite')
		cursor = db.cursor()
		cursor.execute('''SELECT message FROM messages WHERE group_id = ? AND sender_id = ? ORDER BY timestamp DESC LIMIT ?''', (group_id, sender_id, lines))
		rows = cursor.fetchall()
		msg = '以下为[CQ:at,qq=%s]发送的最后%s条记录（如果有）：' % (sender_id, lines)
		for row in rows:
			msg += '\n%s' % (row[0])
		return msg
	except:
		db.close()
		return '[ERROR] Database error'

import requests
import json

def msg_stalker(self_id, group_id, sender_id, lines=5):
	try:
		# It's already cached in CQP client, caching again is redundant
		raw_memberlist = requests.get('http://127.0.0.1:5700/get_group_member_list?group_id={}'.format(group_id)).json()
		memberlist = []
		if raw_memberlist['data']:
			for member in raw_memberlist['data']:
				memberlist.append(str(member['user_id']))
		else:
			return '[ERROR] 目标群号错误或系统故障'
		if str(self_id) in memberlist:
			try:
				db = sqlite3.connect('qqbot.sqlite')
				cursor = db.cursor()
				lines = 20 if int(lines) > 20 else lines
				cursor.execute('''SELECT message FROM messages WHERE group_id = ? AND sender_id = ? ORDER BY timestamp DESC LIMIT ?''', (group_id, sender_id, lines))
				rows = cursor.fetchall()
				msg = '以下为QQ:%s在%s发送的最后%s条记录（如果有）：' % (sender_id, group_id, lines)
				for row in rows:
					msg += '\n%s' % (row[0])
				return msg
			except:
				db.close()
				return '[ERROR] 目标群号错误或系统故障'
		else:
			return '[ERROR] 你不在目标群中，你这个Stalker'
	except:
		return '[ERROR] 目标群号错误或系统故障'

import re
def msg_ar_wrapper(j):
	if j['message'].startswith('/echo'):
		query_id = re.match(r'.*\[CQ:at,qq=(.*)\].*', j['message'])
		if query_id and j['message_type'] == 'group':
			# return msg_fetch(j['group_id'], query_id.group(1))
			return '请私聊机器人 /stalk {} {} 5'.format(j['group_id'], query_id.group(1))

	if j['post_type'] == 'message' and j['message_type'] == 'private':
		if j['message'].startswith('/stalk'):
			query_id = re.match(r'.* (\d+) (\d+) (\d+)', j['message'])
			if query_id:
				return msg_stalker(j['sender']['user_id'], query_id.group(1), query_id.group(2), query_id.group(3))
	
	return ''

def msg_executioner(j):
	if j['message_type'] == 'group':
		try:
			db = sqlite3.connect('qqbot.sqlite')
			cursor = db.cursor()
			cursor.execute('''SELECT timestamp, sender_id FROM messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT 2''', (j['group_id'],))
			rows = cursor.fetchall()
			msg = ''
			if len(rows) == 2:
				timespan = float(rows[0][0]) - float(rows[1][0])
				if timespan > 180 and rows[0][1] == rows[1][1] and random.randint(1, 10) == 1:
					msg = random.choice(['哦', '这样', '真的吗', '挽尊', '然后呢', '嗯嗯'])
			return msg
		except:
			db.close()
			return ''
	return ''

def msg_nature_of_humanity(j):
	if j['message_type'] == 'group':
		try:
			db = sqlite3.connect('qqbot.sqlite')
			cursor = db.cursor()
			cursor.execute('''SELECT message, sender_id FROM messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT 3''', (j['group_id'],))
			rows = cursor.fetchall()
			msg = ''
			# Exactly 3 messages, last two messages are identical, last third is not.
			# Repeat the last message, and ensure repeating only once.
			if len(rows) == 3:
				messages = [rows[0][0], rows[1][0], rows[2][0]]
				senders = [rows[0][1], rows[1][1], rows[2][1]]
				if messages[0] == messages[1] and messages[1] != messages[2] and senders[0] != senders[1]:
					msg = rows[0][0]
					return msg
		except:
			db.close()
			return ''
	return ''

import urllib.parse
def let_me_baidu_that_for_you(j):
	msg = ''
	keyword = j['message'][3:23].strip()
	skip = ['', '呀', '啊', '哇', '一下', '一下你就知道']
	if keyword in skip:
		return ''
	if j['message_type'] == 'group':
		msg = '请点击以下链接直达百度搜索“{}”：\nhttps://www.baidu.com/s?ie=utf8&wd={}'.format(keyword, urllib.parse.quote_plus(keyword))
	return msg

def music_share(j):
	msg = ''
	if j['message_type'] == 'group':
		song_name = j['message'][2:22].strip()
		try:
			data = requests.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp?g_tk=5381&p=1&n=20&w={}&format=json&loginUin=0&hostUin=0&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&remoteplace=txt.yqq.song&t=0&aggr=1&cr=1&catZhida=1'.format(song_name)).json()
			msg = '[CQ:music,type=qq,id={}]'.format(data['data']['song']['list'][0]['songid'])
		except:
			try:
				data = requests.get('https://api.mlwei.com/music/api/wy/?key=523077333&id={}&type=so&cache=0&nu=1'.format(song_name)).json()
				msg = '[CQ:music,type=163,id={}]'.format(data['Body'][0]['id'])
			except:
				msg = '[ERROR]点歌失败，网络错误'
	return msg

import json
import os
with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\tarot.json', 'r', encoding='utf-8') as E:
	tarot_deck = json.loads(E.read())

def draw_tarot(j):
	msg = ''
	draw_num = re.match(r'.* (\d)', j['message'])
	try:
		if draw_num:
			chosen_card = random.sample(tarot_deck, int(draw_num.group(1)))
			for card in chosen_card:
				msg += card['name'] + '\n'
				if random.randint(0, 1) == 0:
					msg += card['desc'] + '\n'
				else:
					msg += card['rdesc'] + '\n'
				msg += '\n'
			msg = msg[:-2]
		else:
			raise ValueError('No match')
	except:
		chosen_card = random.choice(tarot_deck)
		msg = chosen_card['name'] + '\n'
		if random.randint(0, 1) == 0:
			msg += chosen_card['desc']
		else:
			msg += chosen_card['rdesc']

	return msg