import random

def food(meal):
	dishlist = {
		'general': ['炒饭', '炒面', '泡面', '煮面', '匹萨'],
		'breakfast': ['油条', '一般米线', '一般饵丝', '浆米线', '浆饵丝', '小锅米线', '小锅饵丝', '阉鸡米线(热)', '阉鸡米线(冷)', '扒肉米线', '扒肉饵丝', '昨晚的剩饭', '锅贴', '生煎', '冷面', '冷馄饨', '小笼', '煎饼果子'],
		'lunch': ['宫保鸡丁', '过桥米线', '扬州狮子头', '腌笃鲜', '冒菜', '缅甸菜', '赛百味低脂减肥餐'],
		'dinner': ['馒头', '过桥米线', '火锅', '傣族菜', '漆油鸡', '柠檬撒']
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

	return selected_dishes

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