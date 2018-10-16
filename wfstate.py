# -*- coding: utf-8 -*-

import requests
import requests_cache
import os
import json
import time
import math

# Get world state json
# Usage: get_worldstate()
# Return: a very complicated nested array

requests_cache.install_cache('worldstate_cache',expire_after=60)

def get_worldstate():
    wsurl = 'http://content.warframe.com/dynamic/worldState.php'
    ws = requests.get(wsurl).json()
    return ws

# Dictionaries!
with open(os.path.dirname(os.path.abspath(__file__)) + '\\solNodes.json', 'r', encoding='utf-8') as E:
    S = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\languages.json', 'r', encoding='utf-8') as E:
    L = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\missionTypes.json', 'r', encoding='utf-8') as E:
    M = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\sortieBoss.json', 'r', encoding='utf-8') as E:
    B = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\sortieModifier.json', 'r', encoding='utf-8') as E:
    SM = json.loads(E.read())

# Useful functions
def s2h(seconds):
    if seconds >= 86400:
        return str(math.floor(seconds / 86400)) + '天'
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '%d:%02d:%02d' % (h, m, s)
    else:
        return '%02d:%02d' % (m, s)

# User queries:

# Alerts
# Usage: get_alerts()
# Return: a formatted string which contains current alerts

def get_alerts():
    try:
        ws = get_worldstate()
    except:
        return '[ERROR] 获取世界状态失败'
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

        alert_text += '\n\n地点：' + S[alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + M[alert['MissionInfo']['missionType']]['value'] \
        + '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
        + '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
        + '\n时限：' + s2h(expiry)
    return alert_text

# Invasions
def get_invasions():
    return '[ERROR] 功能开发中，敬请期待'


# Fissures
def get_fissures():
    try:
        ws = get_worldstate()
    except:
        return '[ERROR] 获取世界状态失败'
    fissure_text = ''
    fissure_sorted = {
        'VoidT1': [],
        'VoidT2': [],
        'VoidT3': [],
        'VoidT4': []
    }
    fissures = ws['ActiveMissions']
    for fissure in fissures:
        fissure_sorted[fissure['Modifier']].append(fissure)
    for fissure in fissure_sorted['VoidT1']:
        fissure_text += '古纪(T1)：' + S[fissure['Node']]['value'] + ' | ' + M[fissure['MissionType']]['value'] \
        + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT2']:
        fissure_text += '前纪(T2)：' + S[fissure['Node']]['value'] + ' | ' + M[fissure['MissionType']]['value'] \
        + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT3']:
        fissure_text += '中纪(T3)：' + S[fissure['Node']]['value'] + ' | ' + M[fissure['MissionType']]['value'] \
        + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT4']:
        fissure_text += '后纪(T4)：' + S[fissure['Node']]['value'] + ' | ' + M[fissure['MissionType']]['value'] \
        + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    return fissure_text[:-2]

# Sorties
# Usage: get_sorties()
# Return: a formatted string which contains today's sorties

def get_sorties():
    try:
        ws = get_worldstate()
    except:
        return '[ERROR] 获取世界状态失败' 
    sorties = ws['Sorties'][0]['Variants']
    sortie_level = ['50-60', '65-80', '80-100']
    sorties_text = '突击BOSS：' + B[ws['Sorties'][0]['Boss']]
    for i in range(3):
        sorties_text += '\n\n等级：' + sortie_level[i] \
        + '\n地点：' + S[sorties[i]['node']]['value'] \
        + '\n任务：' + M[sorties[i]['missionType']]['value'] \
        + '\n限制：' + SM[sorties[i]['modifierType']]
    return sorties_text


# Cetus
# Usage: get_cetus_time()
# Return: a string about cetus time

def get_cetus_time():
    try:
        ws = get_worldstate()
    except:
        return '[ERROR] 获取世界状态失败'
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

# Automatic broadcasting:

# Cetus day/night transition within 60 seconds
def get_cetus_transition():
    try:
        ws = get_worldstate()
    except:
        return ''
    activation = 0
    for syndicate in ws['SyndicateMissions']:
        if syndicate['Tag'] == 'CetusSyndicate':
            activation = syndicate['Activation']['$date']['$numberLong']
    sec_remain = (150 * 60) - (time.time() - float(activation) / 1000)
    if sec_remain > 50 * 60 and sec_remain < 51 * 60: # 1 min before night
        return '希图斯将于1分钟后进入夜晚。'
    elif sec_remain > 0 and sec_remain < 60: # 1 min before day
        return '希图斯将于1分钟后进入白天。'
    else:
        return ''    
    return ''

# Alerts appeared within 60 seconds
def get_new_alerts():
    try:
        ws = get_worldstate()
    except:
        return ''
    alert_text = ''
    alerts = ws['Alerts']
    for alert in alerts:
        activation = time.time() - float(alert['Activation']['$date']['$numberLong']) / 1000 
        if activation < 60 and activation > 0:
            expiry = float(alert['Expiry']['$date']['$numberLong']) / 1000 - time.time()
            req_archwing = 'Archwing' if 'archwingRequired' in alert['MissionInfo'] else ''
            rew_credits = alert['MissionInfo']['missionReward']['credits']
            rew_items = ' - ' + L[alert['MissionInfo']['missionReward']['items'][0].lower()]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
            rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
            + ' x ' + str(L[alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
            if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

            alert_text += '新警报任务！\n\n地点：' + S[alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + M[alert['MissionInfo']['missionType']]['value'] \
            + '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
            + '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
            + '\n时限：' + s2h(expiry)
    return alert_text