# -*- coding: utf-8 -*-

from qqbot import qqbotsched
import wfstate as wf
import os
import json

with open(os.path.dirname(os.path.abspath(__file__)) + '\\customReplies.json', 'r', encoding='utf-8') as E:
    R = json.loads(E.read())

def onQQMessage(bot, contact, member, content):
    if bot.isMe(contact, member):
        return
    if content == '警报':
        bot.SendTo(contact, wf.get_alerts())
    elif content == '平原时间':
        bot.SendTo(contact, wf.get_cetus_time())
    elif content == '突击':
        bot.SendTo(contact, wf.get_sorties())        
    elif content == '帮助':
        bot.SendTo(contact, '目前可用命令：\n帮助、警报、平原时间、突击')
    elif content.lower().replace(' ','') in R:
        bot.SendTo(contact, R[content.lower().replace(' ','')])

# Reserved for new alerts
#@qqbotsched(second='00,30')
#def mytask(bot):
#    gl = bot.List('group', '')
#    if gl is not None:
#        for group in gl:
#            msg = wf.get_new_alerts()
#            if msg != '':
#                bot.SendTo(group, msg)