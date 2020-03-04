# -*- coding: utf-8 -*-

import json
import math
import os
import random
import re
import time
import urllib.parse

import requests
import requests_cache
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process

requests_cache.install_cache('worldstate_cache', expire_after=60)


def get_worldstate():
    """Get world state json.

    Return a very complicated nested array
    """
    wsurl = 'http://content.warframe.com/dynamic/worldState.php'
    ws = requests.get(wsurl, timeout=30).json()
    return ws


data_files = {
    'solNodes.json': 'S',
    'languages.json': 'L',
    'missionTypes.json': 'M',
    'sortieBoss.json': 'B',
    'sortieModifier.json': 'SM',
    'riven.json': 'R',
    'customReplies.json': 'CR',
    'wm.json': 'WM',
    'wm-parody.json': 'WP',
    'jobs.json': 'J',
    'modlist.json': 'ML',
    'weapon.json': 'W',
    'relic_rewards.json': 'RR',
    'prime_parts.json': 'PP',
}

data_dict = {}

for k in data_files:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'data' ,k) , 'r', encoding='utf-8') as E:
    # with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\' + k, 'r', encoding='utf-8') as E:
        data_dict[data_files[k]] = json.loads(E.read())

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


def s2h(seconds):
    """Convert seconds to D/HH/MM/SS format."""
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


def get_alerts():
    """Get current alerts.

    Return a formatted string which contains current alerts.
    """
    try:
        ws = get_worldstate()
    except BaseException:
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
            rew_items = ' - ' + data_dict['L'][alert['MissionInfo']['missionReward']['items'][
                0].lower()]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
        except BaseException:
            rew_items = ' - ' + \
                alert['MissionInfo']['missionReward']['items'][0] if 'items' in alert['MissionInfo']['missionReward'] else ''
        try:
            rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
                + ' x ' + str(data_dict['L'][alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
                if 'countedItems' in alert['MissionInfo']['missionReward'] else ''
        except BaseException:
            rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
                + ' x ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()) \
                if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

        alert_text += '\n\n地点：' + data_dict['S'][alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + data_dict['M'][alert['MissionInfo']['missionType']]['value'] \
            + '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
            + '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
            + '\n时限：' + s2h(expiry)
    return alert_text


def get_invasions():
    """Get current invasions.

    Return a formatted string which contains current invasions.
    """
    inv_factions = {
        'FC_INFESTATION': 'Infested',
        'FC_CORPUS': 'Corpus',
        'FC_GRINEER': 'Grineer'
    }
    msg = ''
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    invasions = ws['Invasions']
    for invasion in invasions:
        if invasion['Completed'] == 1:
            continue
        inv_vs_infestation = True if invasion['DefenderMissionInfo']['faction'] == 'FC_INFESTATION' else False
        goal_perc = (1 + (float(invasion['Count']) / float(invasion['Goal']))) * (
            100 if inv_vs_infestation else 50)
        try:
            eta_finish = (int(invasion['Goal']) - abs(int(invasion['Count']))) * ((time.time() - float(
                invasion['Activation']['$date']['$numberLong']) / 1000) / abs(int(invasion['Count'])))
        except BaseException:
            eta_finish = 0
        atk_faction = invasion['DefenderMissionInfo']['faction']
        def_faction = invasion['AttackerMissionInfo']['faction']
        atk_reward = data_dict['L'][invasion['AttackerReward']['countedItems'][0]['ItemType'].lower(
        )]['value'] if 'countedItems' in invasion['AttackerReward'] else ''
        atk_reward_q = ' x ' + str(invasion['AttackerReward']['countedItems'][0][
                                   'ItemCount']) if 'countedItems' in invasion['AttackerReward'] else ''
        def_reward = data_dict['L'][invasion['DefenderReward']['countedItems'][0]['ItemType'].lower(
        )]['value'] if 'countedItems' in invasion['DefenderReward'] else ''
        def_reward_q = ' x ' + str(invasion['DefenderReward']['countedItems'][0][
                                   'ItemCount']) if 'countedItems' in invasion['DefenderReward'] else ''

        msg += '地点：' + data_dict['S'][invasion['Node']]['value'] + '\n' + '阵营：' + inv_factions[atk_faction] + ' vs ' + inv_factions[def_faction] + \
            ' (' + data_dict['L'][invasion['LocTag'].lower()]['value'] + ')\n' + \
               '进度：' + '%.2f%% (ETA: %s)' % (goal_perc, s2h(eta_finish)) + '\n'

        if inv_vs_infestation:
            msg += '奖励：' + def_reward + def_reward_q + '\n'
        else:
            msg += '奖励：' + atk_reward + atk_reward_q + \
                ' vs ' + def_reward + def_reward_q + '\n'

        msg += '\n'
    return msg[:-2]


def get_fissures():
    """Get current void fissures.

    Return a formatted string which contains current void fissures.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    fissure_text = ''
    fissure_sorted = {
        'VoidT1': [],
        'VoidT2': [],
        'VoidT3': [],
        'VoidT4': [],
        'VoidT5': []
    }
    fissures = ws['ActiveMissions']
    for fissure in fissures:
        fissure_sorted[fissure['Modifier']].append(fissure)

    for fissure in fissure_sorted['VoidT1']:
        fissure_text += '古纪(T1)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']
                                                                                                      ]['value'] + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT2']:
        fissure_text += '前纪(T2)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']
                                                                                                      ]['value'] + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT3']:
        fissure_text += '中纪(T3)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']
                                                                                                      ]['value'] + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT4']:
        fissure_text += '后纪(T4)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']
                                                                                                      ]['value'] + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'
    for fissure in fissure_sorted['VoidT5']:
        fissure_text += '安魂(T5)：' + data_dict['S'][fissure['Node']]['value'] + ' | ' + data_dict['M'][fissure['MissionType']
                                                                                                      ]['value'] + '\n时限：' + s2h(float(fissure['Expiry']['$date']['$numberLong']) / 1000 - time.time()) + '\n\n'

    return fissure_text[:-2]


def get_sorties():
    """Get today's sortie missions.

    Return a formatted string which contains today's sorties.
    """
    try:
        ws = get_worldstate()
    except BaseException:
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
    """Get cetus time.

    Return a string about cetus time.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    day_cycle_text = ''
    cetus_expiry = 0
    for syndicate in ws['SyndicateMissions']:
        if syndicate['Tag'] == 'CetusSyndicate':
            cetus_expiry = syndicate['Expiry']['$date']['$numberLong']
    cetus_sec_remain = (float(cetus_expiry) / 1000 - time.time()) % 9000 # When it's over 9000!
    if cetus_sec_remain > 50 * 60:  # not night
        day_cycle_text = '希图斯当前是白天，剩余时间' + s2h(cetus_sec_remain - 3000) + '。'
    elif cetus_sec_remain > 0:
        day_cycle_text = '希图斯当前是夜晚，剩余时间' + s2h(cetus_sec_remain) + '。'
    else:
        return '[ERROR] 无法获取平原时间。'
    return day_cycle_text


def get_fortuna_time():
    """Get fortuna time.

    Return a string about Orb Vallis weather.
    Cycle in seconds: 400(Warm) - 400(Cold) - 467(Freezing) - 333(Cold).
    """
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


def get_plains_time():
    """Get time information for both plains.

    Return get_cetus_time() + get_fortuna_time().
    """
    return '{}\n{}'.format(get_cetus_time(), get_fortuna_time())


def get_riven_info(j):
    """Get a random riven.

    A wrapper for riven_details().
    Has the same drop rate distribution as official Sortie drop table.
    """
    # Riven info copied from: https://semlar.com/rivencalc
    weapon = j['message'].replace(j['keyword'], '').strip()
    riven_info = ''
    prefix = ''

    riven_category = {
        '近战': 'Melee',
        '步枪': 'Rifle',
        '手枪': 'Pistol',
        '霰弹枪': 'Shotgun',
        'Zaw': 'Zaw',
        'Kitgun': 'Kitgun'
    }

    if weapon.lower() in data_dict['W']:
        weapon = data_dict['W'][weapon.lower()].upper()

    if weapon in riven_weapons:
        prefix = '你直接从中枢Samodeus那里收到了：\n'
        riven_info = riven_details(
            weapon, random.randint(2, 3), random.randint(0, 1))
    else:
        if weapon in riven_category:
            weapon = riven_category[weapon]
        else:
            weapon = random.choices(
                population=[
                    'Melee',
                    'Rifle',
                    'Pistol',
                    'Shotgun',
                    'Zaw',
                    'Kitgun'],
                weights=[
                    8.14,
                    6.79,
                    7.61,
                    1.36,
                    2.0,
                    2.0],
                k=1).pop()
        prefix = '你从虚空中获得了一张%s裂罅Mod并开出了：\n' % (riven_type[weapon])
        riven_info = riven_details(
            random.sample(
                list(
                    riven_data[weapon]['dispo']), 1)[0], random.randint(
                2, 3), random.randint(
                    0, 1))

    if j['message'].replace('模拟开卡', '').strip() == '卡':
        prefix = prefix.replace('裂罅Mod', '紫色卡卡')
    return prefix + riven_info


def riven_details(weapon, buffs, has_curse, simulate=0):
    """Generate riven detail for given weapon and arguments.

    Parameters
    ----------
    weapon: str
        Weapon name in UPPERCASE.
    buffs: int
        How many buffs, 2 or 3.
    has_curse: int
        How many curses, 0 or 1.
    simulate: int
        WIP: 1 to print all possible ranges.

    Returns
    -------
    str
        Riven detail.
    """
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
        rand_coh[i] = random.random() * 0.2 + 0.9
    rand_coh.sort(reverse=True)
    rand_coh[3] = random.random() * 0.2 + 0.9
    if buffs == 2:
        if has_curse:
            dispo = curr_dispo[weapon] * 1.25
            dispo = dispo * 0.66 * 1.5
            buffs = random.sample(list(curr_buff), 2)
            temp_curr_curse = list(curr_curse)
            for buff in buffs:
                try:
                    temp_curr_curse.remove(buff)
                except BaseException:
                    pass
            curse = random.sample(temp_curr_curse, 1)
            riven_info = '{} {}{}{}\n{} [{}]\n{} [{}]\n{} [{}]'.format(
                data_dict['W']['zh-cn'][weapon.lower().replace(' ', '')],
                curr_prefix[buffs[0]],
                curr_suffix[buffs[1]].lower(),
                riven_dispo_icon(curr_dispo[weapon]),
                buffs[0].replace('|val|', str(
                    round(rand_coh[0] * curr_buff[buffs[0]] * dispo, 2))),
                riven_rank(round((rand_coh[0] - 1) * 100, 2)),
                buffs[1].replace('|val|', str(
                    round(rand_coh[1] * curr_buff[buffs[1]] * dispo, 2))),
                riven_rank(round((rand_coh[1] - 1) * 100, 2)),
                curse[0].replace('|val|', str(-1 * round(rand_coh[2] *
                                                         curr_curse[curse[0]] * curr_dispo[weapon] * 1.5 * 0.33, 2))),
                riven_rank(round((rand_coh[2] - 1) * 100, 2))
            )
        else:
            dispo = curr_dispo[weapon]  # 裂罅倾向
            dispo = dispo * 0.66 * 1.5  # 2buff，无负，按照0.66，1.5紫卡系数
            buffs = random.sample(list(curr_buff), 2)  # 下限系数0.9，上限系数1.1
            riven_info = '{} {}{}{}\n{} [{}]\n{} [{}]'.format(
                data_dict['W']['zh-cn'][weapon.lower().replace(' ', '')],
                curr_prefix[buffs[0]],
                curr_suffix[buffs[1]].lower(),
                riven_dispo_icon(curr_dispo[weapon]),
                buffs[0].replace('|val|', str(
                    round(rand_coh[0] * curr_buff[buffs[0]] * dispo, 2))),
                riven_rank(round((rand_coh[0] - 1) * 100, 2)),
                buffs[1].replace('|val|', str(
                    round(rand_coh[1] * curr_buff[buffs[1]] * dispo, 2))),
                riven_rank(round((rand_coh[1] - 1) * 100, 2))
            )
    elif buffs == 3:
        if has_curse:
            dispo = curr_dispo[weapon] * 1.25
            dispo = dispo * 0.5 * 1.5
            buffs = random.sample(list(curr_buff), 3)
            temp_curr_curse = list(curr_curse)
            for buff in buffs:
                try:
                    temp_curr_curse.remove(buff)
                except BaseException:
                    pass
            curse = random.sample(temp_curr_curse, 1)
            riven_info = '{} {}{}{}\n{} [{}]\n{} [{}]\n{} [{}]\n{} [{}]'.format(
                data_dict['W']['zh-cn'][weapon.lower().replace(' ', '')],
                curr_prefix[buffs[0]],
                curr_suffix[buffs[1]].lower(),
                riven_dispo_icon(curr_dispo[weapon]),
                buffs[0].replace('|val|', str(
                    round(rand_coh[0] * curr_buff[buffs[0]] * dispo, 2))),
                riven_rank(round((rand_coh[0] - 1) * 100, 2)),
                buffs[1].replace('|val|', str(
                    round(rand_coh[1] * curr_buff[buffs[1]] * dispo, 2))),
                riven_rank(round((rand_coh[1] - 1) * 100, 2)),
                buffs[2].replace('|val|', str(
                    round(rand_coh[2] * curr_buff[buffs[2]] * dispo, 2))),
                riven_rank(round((rand_coh[2] - 1) * 100, 2)),
                curse[0].replace('|val|', str(-1 * round(rand_coh[3] *
                                                         curr_curse[curse[0]] * curr_dispo[weapon] * 1.5 * 0.5, 2))),
                riven_rank(round((rand_coh[3] - 1) * 100, 2))
            )
        else:
            dispo = curr_dispo[weapon]
            dispo = dispo * 0.5 * 1.5
            buffs = random.sample(list(curr_buff), 3)
            riven_info = '{} {}{}{}\n{} [{}]\n{} [{}]\n{} [{}]'.format(
                data_dict['W']['zh-cn'][weapon.lower().replace(' ', '')],
                curr_prefix[buffs[0]],
                curr_suffix[buffs[1]].lower(),
                riven_dispo_icon(curr_dispo[weapon]),
                buffs[0].replace('|val|', str(
                    round(rand_coh[0] * curr_buff[buffs[0]] * dispo, 2))),
                riven_rank(round((rand_coh[0] - 1) * 100, 2)),
                buffs[1].replace('|val|', str(
                    round(rand_coh[1] * curr_buff[buffs[1]] * dispo, 2))),
                riven_rank(round((rand_coh[1] - 1) * 100, 2)),
                buffs[2].replace('|val|', str(
                    round(rand_coh[2] * curr_buff[buffs[2]] * dispo, 2))),
                riven_rank(round((rand_coh[2] - 1) * 100, 2))
            )
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


def get_bounties(category):
    """Get current bounties and rotation time.

    Parameters
    ----------
    category: str
        Only accept 'cetus' or 'solaris'. Vox Solaris WIP.

    Returns
    -------
    str
        Bounty information.
    """
    try:
        ws = get_worldstate()
    except BaseException:
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
    """Get current Cetus bounties and rotation time.

    Returns a string.
    """
    return get_bounties('cetus')


def get_bounties_solaris():
    """Get current Solaris bounties and rotation time.

    Returns a string.
    """
    return get_bounties('solaris')


def get_voidtrader():
    """Get current void trader stock or relay of his next arrival.

    Returns a string.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    msg = ''
    vt = ws['VoidTraders'][0]
    # Void Trader is here
    if float(vt['Activation']['$date']['$numberLong']) / 1000 - time.time(
    ) < 0 and float(vt['Expiry']['$date']['$numberLong']) / 1000 - time.time() > 0:
        inv = vt['Manifest']
        msg = '奸商目前已抵达{}，还有{}离开，本次携带物品：'.format(data_dict['S'][vt['Node']]['value'], s2h(
            float(vt['Expiry']['$date']['$numberLong']) / 1000 - time.time()))
        for item in inv:
            try:
                msg += '\n物品：{} DK：{} CR：{}'.format(data_dict['L'][item['ItemType'].lower(
                )]['value'], item['PrimePrice'], item['RegularPrice'])
            except BaseException:
                msg += '\n物品：{} DK：{} CR：{}'.format(
                    item['ItemType'], item['PrimePrice'], item['RegularPrice'])
    else:
        msg = '奸商将于{}后到达{}。'.format(s2h(float(
            vt['Activation']['$date']['$numberLong']) / 1000 - time.time()), data_dict['S'][vt['Node']]['value'])
    return msg


def get_dailydeal():
    """Get current daily deals.

    Clem.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    msg = ''
    dd = ws['DailyDeals'][0]
    try:
        msg += '今日特惠物品：{}，打折-{}%，原价{}白金，现价{}白金，剩余{}/{}。'.format(data_dict['L'][dd['StoreItem'].lower(
        )]['value'] if dd['StoreItem'].lower() in data_dict['L'] else dd['StoreItem'], dd['Discount'], dd['OriginalPrice'], dd['SalePrice'], int(dd['AmountTotal']) - int(dd['AmountSold']), dd['AmountTotal'])
    except BaseException:
        pass
    return msg


def get_acolytes():
    """Get currently appeared acolytes.

    Returns a string.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    msg = ''
    ac = ws['PersistentEnemies']
    if len(ac) > 0:
        msg = '当前出现的追随者：\n'
        for acolyte in ac:
            msg += '【{}】\n状态：{}\n位置：{}\n生命：{:2.2f}%\n\n'.format(data_dict['L'][acolyte['LocTag'].lower()]['value'],
                                                                '出现' if acolyte['Discovered'] else '未知',
                                                                data_dict['S'][acolyte['LastDiscoveredLocation']
                                                                               ]['value'] if acolyte['Discovered'] else '未知',
                                                                float(acolyte['HealthPercent']) * 100)
        msg = msg[:-2]
    else:
        msg = '当前出现的追随者：无'
    return msg


def get_some_help():
    # I NEED THIS SO BAD SOMEONE PLEASE
    return '目前可用命令：\n帮助、警报、入侵、平原时间、地球赏金、金星赏金、突击、裂缝、奸商、遗物、出处、每日特惠、模拟开卡、小小黑'

# Automatic broadcasting:


def get_cetus_transition():
    """BROADCASTING - Cetus transition in 1 minute.

    Returns a string.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return ''
    expiry = 0
    for syndicate in ws['SyndicateMissions']:
        if syndicate['Tag'] == 'CetusSyndicate':
            expiry = syndicate['Expiry']['$date']['$numberLong']
    sec_remain = (float(expiry) / 1000 - time.time()) % 9000
    if sec_remain > 50 * 60 and sec_remain < 51 * 60:  # 1 min before night
        return '希图斯将于1分钟后进入夜晚。'
    elif sec_remain > 0 and sec_remain < 60:  # 1 min before day
        return '希图斯将于1分钟后进入白天。'
    else:
        return ''
    return ''


def get_new_alerts():
    """BROADCASTING - Alerts appeared within 1 minute.

    Returns a string.
    """
    try:
        requests_cache.clear()
        ws = get_worldstate()
    except BaseException:
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
                rew_items = ' - ' + data_dict['L'][alert['MissionInfo']['missionReward']['items'][0].lower(
                )]['value'] if 'items' in alert['MissionInfo']['missionReward'] else ''
            except BaseException:
                rew_items = ' - ' + \
                    alert['MissionInfo']['missionReward']['items'][0] if 'items' in alert['MissionInfo']['missionReward'] else ''
            rew_counteditems = ' - ' + str(alert['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) \
                + ' x ' + str(data_dict['L'][alert['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].lower()]['value']) \
                if 'countedItems' in alert['MissionInfo']['missionReward'] else ''

            bc_counteditems = ['泥炭萃取物', '库狛', '库娃', '虚空光体']
            if rew_items == '' or '内融核心' in rew_items:
                if not any(
                        item in rew_counteditems for item in bc_counteditems):
                    break

            alert_text += '新警报任务！\n\n地点：' + data_dict['S'][alert['MissionInfo']['location']]['value'] + ' | ' + req_archwing + data_dict['M'][alert['MissionInfo']['missionType']]['value'] \
                + '\n等级：' + str(alert['MissionInfo']['minEnemyLevel']) + '-' + str(alert['MissionInfo']['maxEnemyLevel']) \
                + '\n奖励：' + str(rew_credits) + ' CR' + rew_items + rew_counteditems\
                + '\n时限：' + s2h(expiry)
    return alert_text


def get_new_acolyte():
    """BROADCASTING - New acolyte appeared within 1 minute.

    Returns a string.
    """
    try:
        ws = get_worldstate()
    except BaseException:
        return ''
    msg = ''
    ac = ws['PersistentEnemies']
    if len(ac) > 0:
        for acolyte in ac:
            ldt = time.time() - \
                float(acolyte['LastDiscoveredTime']
                      ['$date']['$numberLong']) / 1000
            if 0 < ldt < 60:
                msg += '【{}】\n状态：{}\n位置：{}\n生命：{:2.2f}%\n\n'.format(data_dict['L'][acolyte['LocTag'].lower()]['value'],
                                                                    '出现' if acolyte['Discovered'] else '未知',
                                                                    data_dict['S'][acolyte['LastDiscoveredLocation']
                                                                                   ]['value'] if acolyte['Discovered'] else '未知',
                                                                    float(acolyte['HealthPercent']) * 100)
    if msg != '':
        msg = '新出现的追随者：\n' + msg[:-2]
    return msg

# Other things


def get_wmprice(j):
    """Get warframe.market price.

    Parameters
    ----------
    j: dict
        Received payload.

    Returns
    -------
    str
        warframe.market price.
    """
    msg = ''
    item_name = j['message'].replace(j['keyword'], '').strip()
    item_name = item_name.lower().replace(' ', '')
    if item_name in data_dict['WP']:
        msg = random.choice(data_dict['WP'][item_name])
        return msg

    if item_name in data_dict['WM']:
        wmurl = 'https://api.warframe.market/v1/items/{}/orders'.format(data_dict['WM'][item_name])
        try:
            wm = requests.get(wmurl, timeout=30)

            try:
                converted_data = wm.json()
                sellers = {}
                for order in converted_data['payload']['orders']:
                    if order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
                        sellers[order['user']['ingame_name']
                                ] = order['platinum']
                sorted_sellers = sorted(sellers, key=lambda x: (sellers[x], x))
                plat = 0
                count = 0
                msg += '{}({})\n'.format(j['message'].replace(j['keyword'],
                                                              '').strip(), data_dict['WM'][item_name])
                for i in range(0, 5):
                    try:
                        plat += sellers[sorted_sellers[i]]
                        msg += 'ID: ' + \
                            sorted_sellers[i] + ' 售价: ' + \
                            str(sellers[sorted_sellers[i]]) + '\n'
                        count += 1
                    except BaseException:
                        break

                if count == 0:
                    msg += '目前无游戏内在线玩家出售此物品。'
                else:
                    msg += '平均:' + str(plat / count)
            except BaseException:
                return '[ERROR]无法处理WM数据'
        except BaseException:
            return '[ERROR]无法连接到WM'
    else:
        msg = '未找到这项物品，你是不是想查询：'
        for item in process.extract(item_name, list(data_dict['WM']), limit=5):
            msg += '\n{}'.format(item[0])
    return msg


def get_wiki_text(j):
    s = requests_cache.CachedSession(backend='sqlite', cache_name='wiki_cache')
    mod_name = j['message'].replace(j['keyword'], '').strip()
    msg = ''
    if mod_name.lower().replace(' ', '') in data_dict['ML']:
        wikiurl = 'http://warframe.huijiwiki.com/wiki/' + \
            data_dict['ML'][mod_name.lower().replace(' ', '')]
    else:
        return ''
    try:
        wiki = s.get(wikiurl, timeout=30).text
        soup = BeautifulSoup(wiki, features='html.parser')
        data = soup.find('div', {'class': 'mw-parser-output'})
        msg = data.find('p').text.strip()
    except BaseException:
        return ''
    return msg


def get_wiki_link(j):
    msg = ''
    keyword = j['message'].replace(j['keyword'], '', 1).strip()
    if len(keyword) > 1:
        msg = '请点击直达Warframe中文维基搜索页：\nhttps://warframe.huijiwiki.com/index.php?search={}'.format(
            urllib.parse.quote_plus(keyword))
    else:
        msg = r'Warframe Wiki : https://warframe.huijiwiki.com/wiki/%E9%A6%96%E9%A1%B5'
    return msg

def get_random_sortie_reward(j):
    random.seed('{}{}'.format(j['sender']['user_id'], time.strftime('%Y%m%d', time.gmtime())), version=2)
    if random.randint(0, 9) > 1:
        reward = '你打通了突击任务并获得了【{}】。'.format(random.choices(
            population=[
                '步枪紫卡',
                '阿耶檀识Anasa雕像',
                '4000内融核心',
                'Forma',
                '特殊功能槽连接器',
                'Orokin反应堆蓝图',
                'Orokin催化剂蓝图',
                '传说核心',
                '6000赤毒',
                '现金增幅',
                '经验增幅',
                '掉落几率增幅',
                '手枪紫卡',
                '霰弹枪紫卡',
                '近战紫卡',
                'Zaw紫卡',
                'Kitgun紫卡'],
            weights=[
                6.79,
                28.00,
                12.10,
                2.50,
                2.50,
                2.50,
                2.50,
                0.18,
                12.00,
                3.27,
                3.27,
                3.27,
                7.61,
                1.36,
                8.14,
                2.00,
                2.00],
            k=1).pop())
    else:
        reward = '你没有打通突击任务，无任何奖励。'
    random.seed()
    return reward


def get_challenges_daily():
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'

    msg = '当前赛季日常挑战：'

    challenges = ws['SeasonInfo']['ActiveChallenges']
    dailies = []

    for challenge in challenges:
        if ('Daily', True) in challenge.items():
            dailies.append(challenge)

    for daily in dailies:
        msg += '\n挑战：{}\n时限：{}\n'.format(data_dict['L'][daily['Challenge'].lower()]['desc'] if daily['Challenge'].lower() in data_dict['L'] else daily['Challenge'], s2h(float(daily['Expiry']['$date']['$numberLong']) / 1000 - time.time()))

    return msg


def get_challenges_weekly():
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'

    msg = '当前赛季周常挑战：'

    challenges = ws['SeasonInfo']['ActiveChallenges']
    dailies = []

    for challenge in challenges:
        if 'Daily' not in challenge:
            dailies.append(challenge)

    msg += '\n剩余时间：{}'.format(s2h(float(dailies[0]['Expiry']['$date']['$numberLong']) / 1000 - time.time()))

    for daily in dailies:
        msg += '\n挑战：{}\n奖励声望：{}\n'.format(data_dict['L'][daily['Challenge'].lower()]['desc'] if daily['Challenge'].lower() in data_dict['L'] else daily['Challenge'], 5000 if 'hard' in daily['Challenge'].lower() else 3000)

    return msg


def get_challenges_season():
    try:
        ws = get_worldstate()
    except BaseException:
        return '[ERROR] 获取世界状态失败'
    
    msg = '当前赛季结束时间：{}'.format(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(ws['SeasonInfo']['Expiry']['$date']['$numberLong'])/1000)))

    return msg

def get_riven_pricedata():
    """Get riven price history json.

    Return a very complicated nested array
    """
    s = requests_cache.CachedSession(backend='sqlite', cache_name='riven_cache', expire_after=86400)
    url = 'http://n9e5v4d8.ssl.hwcdn.net/repos/weeklyRivensPC.json'
    data = s.get(url, timeout=30).json()
    return data

def get_riven_prices(j):
    '''Riven price for history data Phase 1
    '''
    try:
        data = get_riven_pricedata()
    except BaseException:
        return '[ERROR] 获取裂罅MOD交易统计数据失败。'

    none_cat = {
        "步枪未开": "Rifle Riven Mod",
        "近战未开": "Melee Riven Mod",
        "手枪未开": "Pistol Riven Mod",
        "zaw未开": "Zaw Riven Mod",
        "kitgun未开": "Kitgun Riven Mod",
        "霰弹枪未开": "Shotgun Riven Mod"
    }

    msg = ''
    item_name = j['message'].replace(j['keyword'], '').strip()
    item_name = item_name.lower().replace(' ', '')

    if item_name in data_dict['W']:
        msg += '{}：\n'.format(item_name)
        unavailable = '无此物品数据，可能DE官方API出现错误'
        if data_dict['W'][item_name] == 'none':
            for d in data:
                if d['itemType'] == none_cat[item_name] and d['compatibility'] == None:
                    unavailable = ''
                    msg += '{:.0f}~{:.0f} (平均{:.2f}，中位数{:.1f}，交易热度{:.0f}/100)'.format(d['min'], d['max'], d['avg'], d['median'], d['pop'])
        else:
            for d in data:
                if str(d['compatibility']).replace(' ', '') == data_dict['W'][item_name].upper():
                    unavailable = ''
                    if d['rerolled'] == False:
                        msg += '零洗：{:.0f}~{:.0f} (平均{:.2f}，中位数{:.1f}，交易热度{:.0f}/100)\n'.format(d['min'], d['max'], d['avg'], d['median'], d['pop'])
                    else:
                        msg += '多洗：{:.0f}~{:.0f} (平均{:.2f}，中位数{:.1f}，交易热度{:.0f}/100)\n'.format(d['min'], d['max'], d['avg'], d['median'], d['pop'])
        msg += unavailable
    else:
        msg = '未找到这项物品，你是不是想查询：'
        for item in process.extract(item_name, list(data_dict['W']), limit=5):
            msg += '\n{}'.format(item[0])

    return msg.strip()


def get_relic_rewards(j):
    msg = ''
    match = re.match(r'.* (.+) ([A-Za-z0-9]+)(.*)', j['message'])
    try:
        if match:
            if match.group(1) in data_dict['RR']:
                if match.group(2).upper() in data_dict['RR'][match.group(1)]:
                    if match.group(3).strip() in data_dict['RR'][match.group(1)][match.group(2).upper()]:
                        quality = match.group(3).strip()
                    else:
                        quality = '完整'

                    msg = '{}{}遗物({})：'.format(match.group(1), match.group(2).upper(), quality)

                    for reward in data_dict['RR'][match.group(1)][match.group(2).upper()][quality]:
                        msg += '\n{}({:.2f}%)'.format(reward['itemName'], reward['chance'])
                else:
                    raise NameError()
            else:
                raise NameError()
        else:
            msg = '命令格式：遗物 纪元 代号 品质(可选)，例如：遗物 古纪 A1。'
    except:
        msg = '命令格式：遗物 纪元 代号 品质(可选)，例如：遗物 古纪 A1。'

    return msg


def get_prime_part_drop_from(j):
    msg = ''
    item_name = j['message'].replace(j['keyword'], '').strip()

    if item_name.lower().title() in data_dict['PP']:
        msg = '{}(掉率为完整遗物)：\n{}'.format(item_name.lower().title(), data_dict['PP'][item_name.lower().title()])
    else:
        msg = '未找到这项物品，你是不是想查询：'
        for item in process.extract(item_name, list(data_dict['PP']), limit=5):
            msg += '\n{}'.format(item[0])

    return msg.strip()