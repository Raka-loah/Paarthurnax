# -*- coding: utf-8 -*-

from qqbot import qqbotsched
import wfstate as wf
import os
import json
import time

with open(os.path.dirname(os.path.abspath(__file__)) + '\\customReplies.json', 'r', encoding='utf-8') as E:
	R = json.loads(E.read())

stats = {}
stats['last_sent'] = time.time()
stats['last_wm_query'] = time.time()

def onQQMessage(bot, contact, member, content):
	suffix = '\n更多命令请输入"帮助"。'
	if bot.isMe(contact, member):
		return
	if content == '警报':
		bot.SendTo(contact, wf.get_alerts() + suffix)
	elif content == '平原时间':
		bot.SendTo(contact, wf.get_cetus_time() + '\n' + wf.get_fortuna_time() + suffix)
	elif content == '突击':
		bot.SendTo(contact, wf.get_sorties() + suffix)
	elif content == '地球赏金':
		bot.SendTo(contact, wf.get_bounties('cetus') + suffix)
	elif content == '金星赏金':
		bot.SendTo(contact, wf.get_bounties('solaris') + suffix)
	elif content == '裂缝':
		bot.SendTo(contact, wf.get_fissures() + suffix)        
	elif content == '入侵':
		bot.SendTo(contact, wf.get_invasions() + suffix)  
	elif content.startswith('模拟开卡'):
		if time.time() - stats['last_sent'] > 60:
			bot.SendTo(contact, '[' + member.name + ']' + wf.get_riven_info(content.replace('模拟开卡', '').strip()))
			stats['last_sent'] = time.time()
		else:
			bot.SendTo(contact, '[' + member.name + ']\n' + wf.cooldown())
	elif content == '帮助':
		bot.SendTo(contact, '目前可用命令：\n帮助、警报、平原时间、地球赏金、金星赏金、突击、裂缝')
	elif content.lower().replace(' ','') in R:
		bot.SendTo(contact, R[content.lower().replace(' ','')])
	elif content.startswith('/roll'):
		msg = wf.misc_roll(content)
		if msg != '':
			if contact.ctype == 'group':
				bot.SendTo(contact, '[' + member.name + ']' + msg)
			else:
				bot.SendTo(contact, msg)
	elif content.startswith('/ask'):
		bot.SendTo(contact, wf.ask_8ball(content))
	elif content.startswith('/wm'):
		if time.time() - stats['last_wm_query'] > 10:		
			msg = wf.get_wmprice(content.replace('/wm', '').strip())
			stats['last_wm_query'] = time.time()
		else:
			msg = wf.cooldown()
		if msg != '':
			if contact.ctype == 'group':
				bot.SendTo(contact, '[' + member.name + ']\n' + msg)
			else:
				bot.SendTo(contact, msg)

# It works but is it good to pull data from web every minute?
@qqbotsched(second='00')
def task_new_alert(bot):
   gl = bot.List('group', 'NGA-warframe交流群')
   if gl is not None:
	   for group in gl:
		   msg = wf.get_new_alerts()
		   if msg != '':
			   bot.SendTo(group, msg)
@qqbotsched(second='05')
def task_cetus_transition(bot):
   gl = bot.List('group', 'NGA-warframe交流群')
   if gl is not None:
	   for group in gl:
		   msg = wf.get_cetus_transition()
		   if msg != '':
			   bot.SendTo(group, msg)