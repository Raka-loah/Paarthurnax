# -*- coding: utf-8 -*-

from urllib.request import urlopen
import os
import json
import time
import math

# TODO: cache this!
wsurl = 'http://content.warframe.com/dynamic/worldState.php'
ws = json.loads(urlopen(wsurl).read().decode('utf-8'))

#with open(os.path.dirname(os.path.abspath(__file__)) + '\\ws.json', 'r', encoding='utf-8') as E:
#    ws = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\solNodes.json', 'r', encoding='utf-8') as E:
    S = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\languages.json', 'r', encoding='utf-8') as E:
    L = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\missionTypes.json', 'r', encoding='utf-8') as E:
    M = json.loads(E.read())

# Alerts
# Usage: get_alerts()
# Return: a formatted string which contains current alerts
def s2h(seconds):
    if seconds >= 86400:
        return str(math.floor(seconds / 86400)) + '天'
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '%d:%02d:%02d' % (h, m, s)
    else:
        return '%02d:%02d' % (m, s)

def get_alerts():
    alert_text = ''
    alerts = ws['Alerts']
    alert_text = '当前有警报 ' + str(len(alerts)) + ' 个：'
    for alert in alerts:
        expiry = float(alert['Expiry']['$date']['$numberLong']) / 1000 - time.time()
        req_archwing = 'Archwing' if 'archwingRequired' in alert['MissionInfo'] else ''
        rew_credits = alert['MissionInfo']['missionReward']['credits']
        rew_items = ' - ' + L[alert['MissionInfo']['missionReward']['items'][0].lower()]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
        rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
        + ' x ' + str(L[alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
        if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

        alert_text += '\n\n地点：' + S[alert["MissionInfo"]["location"]]["value"] + " | " + req_archwing + M[alert["MissionInfo"]["missionType"]]["value"] \
        + '\n等级：' + str(alert["MissionInfo"]["minEnemyLevel"]) + "-" + str(alert["MissionInfo"]["maxEnemyLevel"]) \
        + '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
        + '\n时限：' + s2h(expiry)
    return alert_text

# Invasions

# Fissures

# Sorties

# Cetus
def get_cetus_time():
    activation = 0
    for syndicate in ws['SyndicateMissions']:
        if syndicate['Tag'] == 'CetusSyndicate':
            activation = syndicate['Activation']['$date']['$numberLong']
    sec_remain = (150 * 60) - (time.time() - float(activation) / 1000)
    if sec_remain > 50 * 60: # not night
        return '希图斯当前是白天，剩余时间' + s2h(sec_remain - 3000) + '。'
    elif sec_remain > 0:
        return '希图斯当前是夜晚，剩余时间' + s2h(sec_remain) + '。'
    else:
        return '[ERROR] 无法获取平原时间。'