# -*- coding: utf-8 -*-

import requests
import requests_cache
import os
import json
import time
import math
import random
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup

# Get world state json
# Usage: get_worldstate()
# Return: a very complicated nested array

requests_cache.install_cache('worldstate_cache', expire_after=60)

def get_worldstate():
	wsurl = 'http://content.warframe.com/dynamic/worldState.php'
	ws = requests.get(wsurl).json()
	return ws

# Dictionaries!

data_files = {
	'\\solNodes.json': 'S',
	'\\languages.json': 'L',
	'\\missionTypes.json': 'M',
	'\\sortieBoss.json': 'B',
	'\\sortieModifier.json': 'SM',
	'\\riven.json': 'R',
	'\\customReplies.json': 'CR',
	'\\wm.json': 'WM',
	'\\wm-parody.json': 'WP',
	'\\jobs.json': 'J',
	'\\modlist.json': 'ML'
}

data_dict = {}

for k in data_files:
	with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\' + k, 'r', encoding='utf-8') as E:
		data_dict[data_files[k]] = json.loads(E.read())

# Riven data

riven_type = {
	'Melee': '近战',
	'Rifle': '步枪',
	'Pistol': '手枪',
	'Shotgun': '霰弹枪',
	'Zaw': 'Zaw',
	'Kitgun': 'Kitgun'
}

riven_data = {}

riven_weapons = {}

for k in riven_type:
	riven_data[k] = {
		'dispo': {},
		'buff': {},
		'prefix': {},
		'suffix': {},
		'curse': {}
	}
	for weapon in data_dict['R'][k]['Rivens']:
		riven_data[k]['dispo'][weapon['name']] = weapon['disposition']
		riven_weapons[weapon['name']] = k
	for buff in data_dict['R'][k]['Buffs']:
		riven_data[k]['buff'][buff['text']] = buff['value']
		riven_data[k]['prefix'][buff['text']] = buff['prefix']
		riven_data[k]['suffix'][buff['text']] = buff['suffix']
	for curse in data_dict['R'][k]['Buffs']:
		if 'curse' in curse:
			riven_data[k]['curse'][curse['text']] = curse['value']

# Useful functions

def s2h(seconds):
	if seconds <= 0:
		return 'N/A'
	d = 0
	if seconds >= 86400:
		d = math.floor(seconds / 86400)
	seconds = seconds % 86400
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	if d > 0:
		return '%d天%02d:%02d:%02d' % (d, h, m, s)
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
		expiry = float(alert['Expiry']['$date']
					   ['$numberLong']) / 1000 - time.time()
		req_archwing = 'Archwing' if 'archwingRequired' in alert['MissionInfo'] else ''
		rew_credits = alert['MissionInfo']['missionReward']['credits']
		try:
			rew_items = ' - ' + data_dict['L'][alert['MissionInfo']['missionReward']['items'][0].lower()]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
		except:
			rew_items = ' - ' + alert['MissionInfo']['missionReward']['items'][0] if 'items' in alert['MissionInfo']['missionReward'] else ''
		rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
			+ ' x ' + str(data_dict['L'][alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
			if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

		alert_text += '\n\n地点：' + data_dict['S'][alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + data_dict['M'][alert['MissionInfo']['missionType']]['value'] \
			+ '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
			+ '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
			+ '\n时限：' + s2h(expiry)
	return alert_text

# Invasions


def get_invasions():
	inv_factions = {
		'FC_INFESTATION': 'Infested',
		'FC_CORPUS': 'Corpus',
		'FC_GRINEER': 'Grineer'
	}
	msg = ''
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	invasions = ws['Invasions']
	for invasion in invasions:
		if invasion['Completed'] == 1:
			continue
		inv_vs_infestation = True if invasion['DefenderMissionInfo']['faction'] == 'FC_INFESTATION' else False
		goal_perc = (1 + (float(invasion['Count']) / float(invasion['Goal']))) * (
			100 if inv_vs_infestation else 50)
		try:
			eta_finish = (int(invasion['Goal']) - abs(int(invasion['Count']))) * ((time.time() - float(invasion['Activation']['$date']['$numberLong']) / 1000) / abs(int(invasion['Count'])))
		except:
			eta_finish = 0
		atk_faction = invasion['DefenderMissionInfo']['faction']
		def_faction = invasion['AttackerMissionInfo']['faction']
		atk_reward = data_dict['L'][invasion['AttackerReward']['countedItems'][0]['ItemType'].lower(
		)]['value'] if 'countedItems' in invasion['AttackerReward'] else ''
		atk_reward_q = ' x ' + str(invasion['AttackerReward']['countedItems'][0]
								   ['ItemCount']) if 'countedItems' in invasion['AttackerReward'] else ''
		def_reward = data_dict['L'][invasion['DefenderReward']['countedItems'][0]['ItemType'].lower(
		)]['value'] if 'countedItems' in invasion['DefenderReward'] else ''
		def_reward_q = ' x ' + str(invasion['DefenderReward']['countedItems'][0]
								   ['ItemCount']) if 'countedItems' in invasion['DefenderReward'] else ''

		msg += '地点：' + data_dict['S'][invasion['Node']]['value'] + '\n' \
			+ '阵营：' + inv_factions[atk_faction] + ' vs ' + inv_factions[def_faction] + ' (' + data_dict['L'][invasion['LocTag'].lower()]['value'] + ')\n' \
			+ '进度：' + '%.2f%% (ETA: %s)' % (goal_perc, s2h(eta_finish)) + '\n'

		if inv_vs_infestation:
			msg += '奖励：' + def_reward + def_reward_q + '\n'
		else:
			msg += '奖励：' + atk_reward + atk_reward_q + \
				' vs ' + def_reward + def_reward_q + '\n'

		msg += '\n'
	return msg[:-2]


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
		fissure_text += '古纪(T1)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']]['value'] \
			+ '\n时限：' + \
			s2h(float(fissure['Expiry']['$date']
					  ['$numberLong']) / 1000 - time.time()) + '\n\n'
	for fissure in fissure_sorted['VoidT2']:
		fissure_text += '前纪(T2)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']]['value'] \
			+ '\n时限：' + \
			s2h(float(fissure['Expiry']['$date']
					  ['$numberLong']) / 1000 - time.time()) + '\n\n'
	for fissure in fissure_sorted['VoidT3']:
		fissure_text += '中纪(T3)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']]['value'] \
			+ '\n时限：' + \
			s2h(float(fissure['Expiry']['$date']
					  ['$numberLong']) / 1000 - time.time()) + '\n\n'
	for fissure in fissure_sorted['VoidT4']:
		fissure_text += '后纪(T4)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']]['value'] \
			+ '\n时限：' + \
			s2h(float(fissure['Expiry']['$date']
					  ['$numberLong']) / 1000 - time.time()) + '\n\n'
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
	sorties_text = '突击BOSS：' + data_dict['B'][ws['Sorties'][0]['Boss']]
	for i in range(3):
		sorties_text += '\n\n等级：' + sortie_level[i] \
			+ '\n地点：' + data_dict['S'][sorties[i]['node']]['value'] \
			+ '\n任务：' + data_dict['M'][sorties[i]['missionType']]['value'] \
			+ '\n限制：' + data_dict['SM'][sorties[i]['modifierType']]
	return sorties_text


# Cetus
# Usage: get_cetus_time()
# Return: a string about cetus time

def get_cetus_time():
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	day_cycle_text = ''
	cetus_activation = 0
	for syndicate in ws['SyndicateMissions']:
		if syndicate['Tag'] == 'CetusSyndicate':
			cetus_activation = syndicate['Activation']['$date']['$numberLong']
			cetus_expiry = syndicate['Expiry']['$date']['$numberLong']
	cetus_sec_remain = ((float(cetus_expiry) - float(cetus_activation)) /
						1000) - (time.time() - float(cetus_activation) / 1000)
	if cetus_sec_remain > 50 * 60:  # not night
		day_cycle_text = '希图斯当前是白天，剩余时间' + s2h(cetus_sec_remain - 3000) + '。'
	elif cetus_sec_remain > 0:
		day_cycle_text = '希图斯当前是夜晚，剩余时间' + s2h(cetus_sec_remain) + '。'
	else:
		return '[ERROR] 无法获取平原时间。'
	return day_cycle_text

# Fortuna
# Usage: get_fortuna_time()
# Return: a string about Orb Vallis weather
# Note to self: 400(Warm) - 400(Cold) - 467(Freezing) - 333(Cold)


def get_fortuna_time():
	weather_cycle_text = ''
	# 1541837628 and a 36 sec delay
	cycle_remaining = 1600 - ((time.time() - 1541837628 - 36) % 1600)
	if cycle_remaining > 1200:
		weather_cycle_text = '奥布山谷当前天气温暖，将在' + \
			s2h(cycle_remaining - 1200) + '后转为寒冷。'
	elif cycle_remaining > 800:
		weather_cycle_text = '奥布山谷当前天气寒冷，将在' + \
			s2h(cycle_remaining - 800) + '后转为刺骨，' + \
			s2h(cycle_remaining) + '后转为温暖。'
	elif cycle_remaining > 333:
		weather_cycle_text = '奥布山谷当前天气刺骨，将在' + \
			s2h(cycle_remaining - 333) + '后转为寒冷，' + \
			s2h(cycle_remaining) + '后转为温暖。'
	else:
		weather_cycle_text = '奥布山谷当前天气寒冷，将在' + s2h(cycle_remaining) + '后转为温暖。'
	return weather_cycle_text

# Plains time

def get_plains_time():
	return '{}\n{}'.format(get_cetus_time(), get_fortuna_time())

# Riven
# Usage: get_riven_info()
# Return: Various
# Riven info copied from: https://semlar.com/rivencalc

def get_riven_info(j):
	weapon = j['message'].replace('模拟开卡', '').strip()
	riven_info = ''
	prefix = ''

	if weapon in riven_weapons:
		riven_info = riven_details(
			weapon, random.randint(2, 3), random.randint(0, 1))
	else:
		weapon = random.choices(
			population = ['Melee', 'Rifle', 'Pistol', 'Shotgun', 'Zaw', 'Kitgun'],
			weights = [8.14, 6.79, 7.61, 1.36, 2.0, 2.0],
			k=1
		).pop()
		prefix = '你从虚空中获得了一张%s裂罅Mod并开出了：\n' % (riven_type[weapon])
		riven_info = riven_details(random.sample(list(riven_data[weapon]['dispo']), 1)[0], random.randint(2, 3), random.randint(0, 1))

	if j['message'].replace('模拟开卡', '').strip() == '卡':
		prefix = prefix.replace('裂罅Mod', '紫色卡卡')
	return prefix + riven_info


def riven_details(weapon, buffs, has_curse, simulate=0):
	if weapon in riven_weapons:
		curr_dispo = riven_data[riven_weapons[weapon]]['dispo']
		curr_buff = riven_data[riven_weapons[weapon]]['buff']
		curr_curse = riven_data[riven_weapons[weapon]]['curse']
		curr_prefix = riven_data[riven_weapons[weapon]]['prefix']
		curr_suffix = riven_data[riven_weapons[weapon]]['suffix']
	else:
		return ''

	riven_info = ''
	rand_coh = [0, 0, 0, 0]
	for i in range(0, 3):
		rand_coh[i] = random.random()*0.2+0.9
	rand_coh.sort(reverse=True)
	rand_coh[3] = random.random()*0.2+0.9
	if buffs == 2:
		if has_curse:
			dispo = curr_dispo[weapon] * 1.25
			dispo = dispo * 0.66 * 1.5
			buffs = random.sample(list(curr_buff), 2)
			temp_curr_curse = list(curr_curse)
			for buff in buffs:
				try:
					temp_curr_curse.remove(buff)
				except:
					pass
			curse = random.sample(temp_curr_curse, 1)
			riven_info = data_dict['CR']['翻译' + weapon.lower().replace(' ', '')] + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
				+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']'\
				+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']'\
				+ '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[2]*curr_curse[curse[0]]*curr_dispo[weapon]
																* 1.5*0.33, 2))) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']'
		else:
			dispo = curr_dispo[weapon]  # 裂罅倾向
			dispo = dispo * 0.66 * 1.5  # 2buff，无负，按照0.66，1.5紫卡系数
			buffs = random.sample(list(curr_buff), 2)  # 下限系数0.9，上限系数1.1
			riven_info = data_dict['CR']['翻译'+weapon.lower().replace(' ', '')] + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
				+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
				+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))
										  ) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']'
	elif buffs == 3:
		if has_curse:
			dispo = curr_dispo[weapon] * 1.25
			dispo = dispo * 0.5 * 1.5
			buffs = random.sample(list(curr_buff), 3)
			temp_curr_curse = list(curr_curse)
			for buff in buffs:
				try:
					temp_curr_curse.remove(buff)
				except:
					pass
			curse = random.sample(temp_curr_curse, 1)
			riven_info = data_dict['CR']['翻译'+weapon.lower().replace(' ', '')] + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
				+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
				+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']' \
				+ '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']' \
				+ '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[3]*curr_curse[curse[0]]*curr_dispo[weapon]
																* 1.5*0.5, 2))) + ' [' + riven_rank(round((rand_coh[3] - 1)*100, 2)) + ']'
		else:
			dispo = curr_dispo[weapon]
			dispo = dispo * 0.5 * 1.5
			buffs = random.sample(list(curr_buff), 3)
			riven_info = data_dict['CR']['翻译'+weapon.lower().replace(' ', '')] + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
				+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
				+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']' \
				+ '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo, 2))
										  ) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']'
	return riven_info


def riven_rank(perc):
	rank = ''
	if 9.5 < perc <= 10:
		rank = 'SSS'
	elif 9 < perc <= 9.5:
		rank = 'SS'
	elif 6 < perc <= 9:
		rank = 'S'
	elif 2 < perc <= 6:
		rank = 'A'
	elif -2 < perc <= 2:
		rank = 'B'
	elif -6 < perc <= -2:
		rank = 'C'
	elif -10 <= perc <= -6:
		rank = 'D'
	else:
		rank = '?'
	return rank


def riven_dispo_icon(dispo):
	text = ''
	if dispo > 1.3:
		text = '●●●●●'
	elif 1.1 < dispo <= 1.3:
		text = '●●●●○'
	elif 0.9 <= dispo <= 1.1:
		text = '●●●○○'
	elif 0.7 <= dispo < 0.9:
		text = '●●○○○'
	elif dispo < 0.7:
		text = '●○○○○'
	else:
		text = '?'
	return (' %s(%.2f)' % (text, dispo))

# Bounties
# Usage: get_bounties(category) category: 'cetus'/'solaris'
# Return: a very long string about selected bounties

def get_bounties(category):
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	msg = ''
	if category == 'cetus':
		for syndicate in ws['SyndicateMissions']:
			if syndicate['Tag'] == 'CetusSyndicate':
				cetus_bounties = syndicate['Jobs']
				expiry = syndicate['Expiry']['$date']['$numberLong']
		job_count = 0
		msg = '希图斯当前赏金：（' + s2h(float(expiry) / 1000 - time.time()) + '后轮换）\n'
		for job in cetus_bounties:
			job_count += 1
			msg += '赏金' + str(job_count) + ': ' + \
				data_dict['J'][job['rewards'].lower()]['value'] + '\n'
		msg = msg[:-1]
	elif category == 'solaris':
		for syndicate in ws['SyndicateMissions']:
			if syndicate['Tag'] == 'SolarisSyndicate':
				solaris_bounties = syndicate['Jobs']
				expiry = syndicate['Expiry']['$date']['$numberLong']
		job_count = 0
		msg = '索拉里斯联盟当前赏金：（' + \
			s2h(float(expiry) / 1000 - time.time()) + '后轮换）\n'
		for job in solaris_bounties:
			job_count += 1
			msg += '赏金' + str(job_count) + ': ' + \
				data_dict['J'][job['rewards'].lower()]['value'] + '\n'
		msg = msg[:-1]
	else:
		msg = ''
	return msg

def get_bounties_cetus():
	return get_bounties('cetus')

def get_bounties_solaris():
	return get_bounties('solaris')

# Void Trader

def get_voidtrader():
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	msg = ''
	vt = ws['VoidTraders'][0]
	# Void Trader is here
	if float(vt['Activation']['$date']['$numberLong']) / 1000 - time.time() < 0 and float(vt['Expiry']['$date']['$numberLong']) / 1000 - time.time() > 0:
		inv = vt['Manifest']
		msg = '奸商目前已抵达{}，还有{}离开，本次携带物品：'.format(data_dict['S'][vt['Node']]['value'], s2h(float(vt['Expiry']['$date']['$numberLong']) / 1000 - time.time()))
		for item in inv:
			try:
				msg += '\n物品：{} DK：{} CR：{}'.format(data_dict['L'][item['ItemType'].lower()]['value'], item['PrimePrice'], item['RegularPrice'])
			except:
				msg += '\n物品：{} DK：{} CR：{}'.format(item['ItemType'], item['PrimePrice'], item['RegularPrice'])
	else:
		msg = '奸商将于{}后到达{}。'.format(s2h(float(vt['Activation']['$date']['$numberLong']) / 1000 - time.time()), data_dict['S'][vt['Node']]['value'])
	return msg

# Daily Deal

def get_dailydeal():
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	msg = ''
	dd = ws['DailyDeals'][0]
	try:
		msg += '今日特惠物品：{}，打折-{}%，原价{}白金，现价{}白金，剩余{}/{}。'.format(data_dict['L'][dd['StoreItem'].lower()]['value'], dd['Discount'] ,dd['OriginalPrice'], dd['SalePrice'], int(dd['AmountTotal']) - int(dd['AmountSold']), dd['AmountTotal'])
	except:
		pass
	return msg

def get_acolytes():
	try:
		ws = get_worldstate()
	except:
		return '[ERROR] 获取世界状态失败'
	msg = ''
	ac = ws['PersistentEnemies']
	if len(ac) > 0:
		msg = '当前出现的追随者：\n'
		for acolyte in ac:
			msg += '【{}】\n状态：{}\n位置：{}\n生命：{:2.2f}%\n\n'.format(data_dict['L'][acolyte['LocTag'].lower()]['value'], '出现' if acolyte['Discovered'] else '未知', data_dict['S'][acolyte['LastDiscoveredLocation']]['value'] if acolyte['Discovered'] else '未知', float(acolyte['HealthPercent']) * 100)
		msg = msg[:-2]
	else:
		msg = '当前出现的追随者：无'
	return msg

def get_some_help():
	# I NEED THIS SO BAD SOMEONE PLEASE
	return '目前可用命令：\n帮助、警报、入侵、平原时间、地球赏金、金星赏金、突击、裂缝、奸商、每日特惠、模拟开卡、小小黑'

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
	if sec_remain > 50 * 60 and sec_remain < 51 * 60:  # 1 min before night
		return '希图斯将于1分钟后进入夜晚。'
	elif sec_remain > 0 and sec_remain < 60:  # 1 min before day
		return '希图斯将于1分钟后进入白天。'
	else:
		return ''
	return ''

# Alerts appeared within 60 seconds


def get_new_alerts():
	try:
		requests_cache.clear()
		ws = get_worldstate()
	except:
		return ''
	alert_text = ''
	alerts = ws['Alerts']
	for alert in alerts:
		activation = time.time() - \
			float(alert['Activation']['$date']['$numberLong']) / 1000
		if activation < 60 and activation > 0:
			expiry = float(alert['Expiry']['$date']
						   ['$numberLong']) / 1000 - time.time()
			req_archwing = 'Archwing' if 'archwingRequired' in alert['MissionInfo'] else ''
			rew_credits = alert['MissionInfo']['missionReward']['credits']
			try:
				rew_items = ' - ' + data_dict['L'][alert['MissionInfo']['missionReward']['items'][0].lower()]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
			except:
				rew_items = ' - ' + alert['MissionInfo']['missionReward']['items'][0] if 'items' in alert['MissionInfo']['missionReward'] else ''
			rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
				+ ' x ' + str(data_dict['L'][alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
				if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

			bc_counteditems = ['泥炭萃取物', '库狛', '库娃', '虚空光体']
			if rew_items == '' or '内融核心' in rew_items:
				if not any(item in rew_counteditems for item in bc_counteditems):
					break

			alert_text += '新警报任务！\n\n地点：' + data_dict['S'][alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + data_dict['M'][alert['MissionInfo']['missionType']]['value'] \
				+ '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
				+ '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
				+ '\n时限：' + s2h(expiry)
	return alert_text

def get_new_acolyte():
	try:
		ws = get_worldstate()
	except:
		return ''
	msg = ''
	ac = ws['PersistentEnemies']
	if len(ac) > 0:
		for acolyte in ac:
			ldt = time.time() - float(acolyte['LastDiscoveredTime']['$date']['$numberLong']) / 1000
			if 0 < ldt < 60:
				msg += '【{}】\n状态：{}\n位置：{}\n生命：{:2.2f}%\n\n'.format(data_dict['L'][acolyte['LocTag'].lower()]['value'], '出现' if acolyte['Discovered'] else '未知', data_dict['S'][acolyte['LastDiscoveredLocation']]['value'] if acolyte['Discovered'] else '未知', float(acolyte['HealthPercent']) * 100)
	if msg != '':
		msg = '新出现的追随者：\n' + msg[:-2]
	return msg

# Miscellaneous:
# Roll

def misc_roll(j):
	msg = ''

	max_dices = 10
	max_faces = 1000

	# default to 1d100+0
	dice_num = 1
	dice_faces = 100
	dice_modifier = '+'
	dice_modifier_num = 0

	# xdy+z format
	dices = re.match(r'.* (\d+)[dD](\d+)([\+\-])(\d+)', j['message'])
	if dices:
		dice_num = int(dices.group(1)) if int(dices.group(1)) <= max_dices else max_dices
		dice_faces = int(dices.group(2)) if int(dices.group(2)) <= max_faces else max_faces
		dice_modifier = dices.group(3)
		dice_modifier_num = int(dices.group(4))
	else:
		# xdy format
		dices = re.match(r'.* (\d+)[dD](\d+)', j['message'])
		if dices:
			dice_num = int(dices.group(1)) if int(dices.group(1)) <= max_dices else max_dices
			dice_faces = int(dices.group(2)) if int(dices.group(2)) <= max_faces else max_faces
		else:
			# only a number	
			dices = re.match(r'.* (\d+)', j['message'])
			if dices:
				dice_num = 1
				dice_faces = int(dices.group(1)) if int(dices.group(1)) <= max_faces else max_faces

	results = []

	try:
		for _ in range(0, dice_num):
			results.append(random.randint(1, dice_faces))
	except:
		results.append(random.randint(1, 100))

	if len(results) <= 1:
		if dice_modifier_num > 0:
			msg = '{} {} {} = {}'.format(results[0], dice_modifier, dice_modifier_num, results[0] + dice_modifier_num if dice_modifier == '+' else results[0] - dice_modifier_num)
		else:
			msg = str(results[0])
	else:
		if dice_modifier_num > 0:
			msg = '('
			sum_dices = 0
			for result in results:
				msg += str(result) + ','
				sum_dices += result
			msg = msg[:-1]
			msg += ') {} {} = {}'.format(dice_modifier, dice_modifier_num, sum_dices + dice_modifier_num if dice_modifier == '+' else sum_dices - dice_modifier_num)			
		else:
			msg = '('
			sum_dices = 0
			for result in results:
				msg += str(result) + ','
				sum_dices += result
			msg = msg[:-1]
			msg += ') = {}'.format(sum_dices)

	if msg != '':
		if dice_modifier_num > 0:
			return 'Roll({}d{}{}{}): {}'.format(dice_num, dice_faces, dice_modifier, dice_modifier_num, msg)
		else:
			return 'Roll({}d{}): {}'.format(dice_num, dice_faces, msg)
	else:
		return ''

def ask_8ball(j):
	replies = ['当然YES咯', '我觉得OK', '毫无疑问', '妥妥儿的', '你就放心吧', '让我说的话，YES', '基本上没跑了', '看起来没问题', 'YES', '我听卡德加说YES，那就YES吧',
			   '有点复杂，再试一次', '过会儿再问我', '我觉得还是别剧透了', '放飞自我中，过会儿再问', '你心不够诚，再试一次', '我觉得不行', '我必须说NO', '情况不容乐观', '我觉得根本就是NO', '我持怀疑态度']
	return random.choice(replies)


def cooldown():
	replies = ['我还不能施放这个法术', '这个法术还在冷却中', '法术冷却中', '我还没准备好施放这个法术', '被抵抗，请稍后再试']
	return random.choice(replies)

def get_wmprice(j):
	msg = ''
	item_name = j['message'].replace('/wm','').strip()
	item_name = item_name.lower().replace(' ', '')
	if item_name in data_dict['WP']:
		msg = random.choice(data_dict['WP'][item_name])
		return msg

	if item_name in data_dict['WM']:
		wmurl = 'https://warframe.market/items/' + data_dict['WM'][item_name]
		try:
			wm = requests.get(wmurl).text

			soup = BeautifulSoup(wm, features='html.parser')
			data = soup.find('script', id='application-state').text

			try:
				converted_data = json.loads(data)
				sellers = {}
				for order in converted_data['payload']['orders']:
					if order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
						sellers[order['user']['ingame_name']
								] = order['platinum']
				sorted_sellers = sorted(sellers, key=lambda x: (sellers[x], x))
				plat = 0
				count = 0
				msg += '{}({})\n'.format(j['message'].replace('/wm','').strip(), data_dict['WM'][item_name])
				for i in range(0, 5):
					try:
						plat += sellers[sorted_sellers[i]]
						msg += 'ID: ' + \
							sorted_sellers[i] + ' 售价: ' + \
							str(sellers[sorted_sellers[i]]) + '\n'
						count += 1
					except:
						break
				msg += '平均:' + str(plat / count)
			except:
				return '[ERROR]无法处理WM数据'
		except:
			return '[ERROR]无法连接到WM'
	else:
		msg = '未找到这项物品，你是不是想查询：'
		for item in process.extract(item_name, list(data_dict['WM']), limit=5):
			msg += '\n{}'.format(item[0])
	return msg

def get_wiki_text(j):
	s = requests_cache.CachedSession(backend='sqlite', cache_name='wiki_cache')
	mod_name = j['message'].replace('/mod','').strip()
	msg = ''
	if mod_name.lower().replace(' ', '') in data_dict['ML']:
		wikiurl = 'http://warframe.huijiwiki.com/wiki/' + \
			data_dict['ML'][mod_name.lower().replace(' ', '')]
	else:
		return ''
	try:
		wiki = s.get(wikiurl).text
		soup = BeautifulSoup(wiki, features='html.parser')
		data = soup.find('div', {'class': 'mw-parser-output'})
		msg = data.find('p').text.strip()
	except:
		return ''
	return msg

import urllib.parse
def get_wiki_link(j):
	msg = ''
	keyword = j['message'].replace('wiki来', '', 1).strip()
	if len(keyword) > 1:
		msg = '请点击直达Warframe中文维基搜索页：\nhttps://warframe.huijiwiki.com/index.php?search={}'.format(urllib.parse.quote_plus(keyword))
	else:
		msg = r'Warframe Wiki : https://warframe.huijiwiki.com/wiki/%E9%A6%96%E9%A1%B5'
	return msg