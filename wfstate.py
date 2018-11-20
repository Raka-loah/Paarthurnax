# -*- coding: utf-8 -*-

import requests
import requests_cache
import os
import json
import time
import math
import random
from bs4 import BeautifulSoup

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

with open(os.path.dirname(os.path.abspath(__file__)) + '\\riven.json', 'r', encoding='utf-8') as E:
	R = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\customReplies.json', 'r', encoding='utf-8') as E:
	CR = json.loads(E.read())

with open(os.path.dirname(os.path.abspath(__file__)) + '\\wm.json', 'r', encoding='utf-8') as E:
	WM = json.loads(E.read())

melee_dispo = {}
melee_buff = {}
melee_curse = {}
melee_prefix = {}
melee_suffix = {}
for melee in R['Melee']['Rivens']:
	melee_dispo[melee['name']] = melee['disposition']
for buff in R['Melee']['Buffs']:
	melee_buff[buff['text']] = buff['value']
	melee_prefix[buff['text']] = buff['prefix']
	melee_suffix[buff['text']] = buff['suffix']
for curse in R['Melee']['Buffs']:
	if 'curse' in curse:
		melee_curse[curse['text']] = curse['value']

rifle_dispo = {}
rifle_buff = {}
rifle_curse = {}
rifle_prefix = {}
rifle_suffix = {}
for rifle in R['Rifle']['Rivens']:
	rifle_dispo[rifle['name']] = rifle['disposition']
for buff in R['Rifle']['Buffs']:
	rifle_buff[buff['text']] = buff['value']
	rifle_prefix[buff['text']] = buff['prefix']
	rifle_suffix[buff['text']] = buff['suffix']
for curse in R['Rifle']['Buffs']:
	if 'curse' in curse:
		rifle_curse[curse['text']] = curse['value']

shotgun_dispo = {}
shotgun_buff = {}
shotgun_curse = {}
shotgun_prefix = {}
shotgun_suffix = {}
for shotgun in R['Shotgun']['Rivens']:
	shotgun_dispo[shotgun['name']] = shotgun['disposition']
for buff in R['Shotgun']['Buffs']:
	shotgun_buff[buff['text']] = buff['value']
	shotgun_prefix[buff['text']] = buff['prefix']
	shotgun_suffix[buff['text']] = buff['suffix']
for curse in R['Shotgun']['Buffs']:
	if 'curse' in curse:
		shotgun_curse[curse['text']] = curse['value']

pistol_dispo = {}
pistol_buff = {}
pistol_curse = {}
pistol_prefix = {}
pistol_suffix = {}
for pistol in R['Pistol']['Rivens']:
	pistol_dispo[pistol['name']] = pistol['disposition']
for buff in R['Pistol']['Buffs']:
	pistol_buff[buff['text']] = buff['value']
	pistol_prefix[buff['text']] = buff['prefix']
	pistol_suffix[buff['text']] = buff['suffix']
for curse in R['Pistol']['Buffs']:
	if 'curse' in curse:
		pistol_curse[curse['text']] = curse['value']

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
	day_cycle_text = ''
	cetus_activation = 0
	for syndicate in ws['SyndicateMissions']:
		if syndicate['Tag'] == 'CetusSyndicate':
			cetus_activation = syndicate['Activation']['$date']['$numberLong']
			cetus_expiry = syndicate['Expiry']['$date']['$numberLong']
	cetus_sec_remain = ((float(cetus_expiry) - float(cetus_activation)) / 1000) - (time.time() - float(cetus_activation) / 1000)
	if cetus_sec_remain > 50 * 60: # not night
		day_cycle_text = '希图斯当前是白天，剩余时间' + s2h(cetus_sec_remain - 3000) + '。'
	elif cetus_sec_remain > 0:
		day_cycle_text = '希图斯当前是夜晚，剩余时间' + s2h(cetus_sec_remain) + '。'
	else:
		return '[ERROR] 无法获取平原时间。'
	return day_cycle_text

# Fortuna
# Usage: get_fortuna_time()
# Return: a string about Orb Vallis weather

def get_fortuna_time():
	weather_cycle_text = ''
	cycle_remaining = 1600 - ((time.time() - 1541837628 - 36) % 1600) # 1541837628 has a 36 sec delay
	if cycle_remaining > 1200:
		weather_cycle_text = '奥布山谷当前天气温暖，剩余时间' + s2h(cycle_remaining - 1200) + '。'
	else:
		weather_cycle_text = '奥布山谷当前天气寒冷，剩余时间' + s2h(cycle_remaining) + '。'
	return weather_cycle_text

# Riven
# Usage: get_riven_info()
# Return: Various
# Riven info copied from: https://semlar.com/rivencalc

def get_riven_info(weapon, simulate=0):
	riven_info = ''
	prefix = ''
	roll = random.random()
	if weapon in melee_dispo or weapon in rifle_dispo or weapon in shotgun_dispo or weapon in pistol_dispo:
		riven_info = riven_details(weapon,random.randint(2,3),random.randint(0,1))
	elif roll < 0.3915:
		prefix = '你从虚空中获得了一张近战裂罅Mod并开出了：\n'
		riven_info = riven_details(random.sample(list(melee_dispo),1)[0],random.randint(2,3),random.randint(0,1))
	elif roll >= 0.3915 and roll < 0.6853:
		prefix = '你从虚空中获得了一张手枪裂罅Mod并开出了：\n'
		riven_info = riven_details(random.sample(list(pistol_dispo),1)[0],random.randint(2,3),random.randint(0,1))
	elif roll >= 0.6853 and roll < 0.9475:
		prefix = '你从虚空中获得了一张步枪裂罅Mod并开出了：\n'
		riven_info = riven_details(random.sample(list(rifle_dispo),1)[0],random.randint(2,3),random.randint(0,1))
	elif roll >= 0.9475:
		prefix = '你从虚空中获得了一张霰弹枪裂罅Mod并开出了：\n'
		riven_info = riven_details(random.sample(list(shotgun_dispo),1)[0],random.randint(2,3),random.randint(0,1))
	else: #how???
		pass
	if weapon == '卡':
		prefix = prefix.replace('裂罅Mod','紫色卡卡')
	return prefix + riven_info

def riven_details(weapon, buffs, has_curse, simulate=0):
	if weapon in melee_dispo:
		curr_dispo = melee_dispo
		curr_buff = melee_buff
		curr_curse = melee_curse
		curr_prefix = melee_prefix
		curr_suffix = melee_suffix
	elif weapon in rifle_dispo:
		curr_dispo = rifle_dispo
		curr_buff = rifle_buff
		curr_curse = rifle_curse
		curr_prefix = rifle_prefix
		curr_suffix = rifle_suffix
	elif weapon in shotgun_dispo:
		curr_dispo = shotgun_dispo
		curr_buff = shotgun_buff
		curr_curse = shotgun_curse
		curr_prefix = shotgun_prefix
		curr_suffix = shotgun_suffix
	elif weapon in pistol_dispo:
		curr_dispo = pistol_dispo
		curr_buff = pistol_buff
		curr_curse = pistol_curse
		curr_prefix = pistol_prefix
		curr_suffix = pistol_suffix
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
			riven_info = CR['翻译' + weapon.lower().replace(' ','')] + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + '\n' \
			+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo,2))) + ' [' + str(round((rand_coh[0] - 1)*100,2)) + '%]'\
			+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo,2))) + ' [' + str(round((rand_coh[1] - 1)*100,2)) + '%]'\
			+ '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[2]*curr_curse[curse[0]]*curr_dispo[weapon]*1.5*0.33,2))) + ' [' + str(round((rand_coh[2] - 1)*100,2)) + '%]'
		else:
			dispo = curr_dispo[weapon] #裂罅倾向
			dispo = dispo * 0.66 * 1.5 #2buff，无负，按照0.66，1.5紫卡系数
			buffs = random.sample(list(curr_buff),2) #下限系数0.9，上限系数1.1
			riven_info = CR['翻译'+weapon.lower().replace(' ','')] + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + '\n' \
			+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo,2))) + ' [' + str(round((rand_coh[0] - 1)*100,2)) + '%]' \
			+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo,2))) + ' [' + str(round((rand_coh[1] - 1)*100,2)) + '%]'
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
			riven_info = CR['翻译'+weapon.lower().replace(' ','')] + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + '\n' \
			+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo,2))) + ' [' + str(round((rand_coh[0] - 1)*100,2)) + '%]' \
			+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo,2))) + ' [' + str(round((rand_coh[1] - 1)*100,2)) + '%]' \
			+ '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo,2))) + ' [' + str(round((rand_coh[2] - 1)*100,2)) + '%]' \
			+ '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[3]*curr_curse[curse[0]]*curr_dispo[weapon]*1.5*0.5,2))) + ' [' + str(round((rand_coh[3] - 1)*100,2)) + '%]'
		else:
			dispo = curr_dispo[weapon]
			dispo = dispo * 0.5 * 1.5
			buffs = random.sample(list(curr_buff),3)
			riven_info = CR['翻译'+weapon.lower().replace(' ','')] + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + '\n' \
			+ buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo,2))) + ' [' + str(round((rand_coh[0] - 1)*100,2)) + '%]' \
			+ '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo,2))) + ' [' + str(round((rand_coh[1] - 1)*100,2)) + '%]' \
			+ '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo,2))) + ' [' + str(round((rand_coh[2] - 1)*100,2)) + '%]'
	return riven_info


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

			if rew_items == '':
				break

			alert_text += '新警报任务！\n\n地点：' + S[alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + M[alert['MissionInfo']['missionType']]['value'] \
			+ '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
			+ '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
			+ '\n时限：' + s2h(expiry)
	return alert_text

# Miscellaneous:
# Roll
def misc_roll(content):
	try:
		roll_range = int(content.replace('/roll', ''))
	except:
		roll_range = 100
	if roll_range > 1:
		return 'Roll(' + str(roll_range) + '): ' + str(random.randint(1, roll_range))
	return ''

def ask_8ball(content):
	replies = ['当然YES咯','我觉得OK','毫无疑问','妥妥儿的','你就放心吧','让我说的话，YES','基本上没跑了','看起来没问题','YES','我听卡德加说YES，那就YES吧','有点复杂，再试一次','过会儿再问我','我觉得还是别剧透了','放飞自我中，过会儿再问','你心不够诚，再试一次','我觉得不行','我必须说NO','情况不容乐观','我觉得根本就是NO','我持怀疑态度']
	return random.choice(replies)

def cooldown():
	replies = ['我还不能施放这个法术', '这个法术还在冷却中', '法术冷却中', '被抵抗，请稍后再试']
	return random.choice(replies)

def get_wmprice(item_name):
	msg = ''
	item_name = item_name.lower().replace(' ','')
	if item_name in WM:
		wmurl = 'https://warframe.market/items/' + WM[item_name]
		try:
			wm = requests.get(wmurl).text

			soup = BeautifulSoup(wm, features='html.parser')
			data = soup.find('script', id='application-state').text

			try:
				converted_data = json.loads(data)
				sellers = {}
				for order in converted_data['payload']['orders']:
					if order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
						sellers[order['user']['ingame_name']] = order['platinum']
				sorted_sellers = sorted(sellers, key=lambda x: (sellers[x], x))
				plat = 0
				count = 0
				for i in range(0,5):
					try:
						plat += sellers[sorted_sellers[i]]
						msg += 'ID: ' + sorted_sellers[i] + ' 售价: ' + str(sellers[sorted_sellers[i]]) + '\n'
						count += 1
					except:
						break
				msg += '平均:' + str(plat / count)
			except:
				return '[ERROR]无法处理WM数据'
		except:
			return '[ERROR]无法连接到WM'
	return msg