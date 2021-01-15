import json
import os
import random
import sqlite3
import time

card_pools = {}

svts = {}
crafts = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'data' ,'svts.json') , 'r', encoding='utf-8') as E:
    c = json.loads(E.read())
    svts = {x[0] : x for x in c['svts']}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'data' ,'crafts.json') , 'r', encoding='utf-8') as E:
    c = json.loads(E.read())
    crafts = {x[0] : x for x in c['crafts']}

json_files = [j for j in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'rates')) if j.endswith('.json')]

for j in json_files:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'rates' , j), 'r', encoding='utf-8') as E:
        card_pools[j.replace('.json', '')] = json.loads(E.read())

# ^(.+)\t(.+)\t(.+)\t(.+)\t(.+)$
# \["\1", "\2", "\3", "\4", \[\5\]\],

def build_pool(card_pool):
    cards = []
    weights = []
    cards_rare = []
    weights_rare = []
    cards_svt = []
    weights_svt = []
    is_random = False
    if card_pool not in [x for x in card_pools.keys()]:
        card_pool = random.choice([x for x in card_pools.keys()])
        is_random = True

    for entry in card_pools[card_pool]['card_pool']:
        for item in entry[4]:
            if entry[0] == 'svt':
                cards.append([svts[item][1], svts[item][3], svts[item][2]])
                cards_svt.append([svts[item][1], svts[item][3], svts[item][2]])
                weights_svt.append(float(entry[2])/len(entry[4]))
                if int(entry[1]) >= 4:
                     cards_rare.append([svts[item][1], svts[item][3], svts[item][2]])
            elif entry[0] == 'ce':
                cards.append([crafts[item][1], '概念礼装', crafts[item][2]])
                if int(entry[1]) >= 4:
                     cards_rare.append([crafts[item][1], '概念礼装', crafts[item][2]])
            weights.append(float(entry[2])/len(entry[4]))
            if int(entry[1]) >= 4:
                weights_rare.append(float(entry[2])/len(entry[4]))

    return {'is_random': is_random, 'card_pool': card_pool, 'cards': cards, 'weights': weights, 'cards_rare': cards_rare, 'weights_rare': weights_rare, 'cards_svt': cards_svt, 'weights_svt': weights_svt}


def do_pull(j):
    if j['message_type'] != 'group':
        return '抱歉，抽卡仅限指定QQ群内使用。'

    if cd(j['group_id'], j['sender']['user_id']):
        return '距离上次召唤不足10分钟，御主请稍等片刻。'

    card_pool = build_pool(j['message'].replace(j['keyword'], '').strip())

    pull = random.choices(card_pool['cards'], weights=card_pool['weights'], k=9)
    guarantee = random.choices(card_pool['cards_rare'], weights=card_pool['weights_rare'], k=1)
    guarantee_svt = random.choices(card_pool['cards_svt'], weights=card_pool['weights_svt'], k=1)
    pull.extend(guarantee)
    pull.extend(guarantee_svt)
    
    rare_cards = []
    for card in pull:
        if int(card[0]) > 3 :
            rare_cards.append(card)

    message = f'从{"随机" if card_pool["is_random"] else ""}卡池【{card_pools[card_pool["card_pool"]]["metadata"]["title"]}】十连抽出了：\n'
    for card in rare_cards:
        message += f'[{"★"*int(card[0])}]！{card[1]}\n“{card[2]}”\n'
    message += '以及其它不重要的东西。'

    return message.strip()

def pools(j):
    message = '当然可用FGO卡池：\n'

    for k, v in card_pools.items():
        message += f'{k}: {v["metadata"]["title"]}\n'

    return message.strip()

def connect():
    try:
        db = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'cd_fgo.sqlite'))
        cursor = db.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS cd(group_id INTEGER, user_id INTEGER, lastpull REAL)''')
        db.commit()
    except Exception as e:
        db.rollback()
        db.close()
        print(e)
        return '[ERROR] Database error'

    return db

def cd(group_id, user_id):
    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute('select lastpull from cd where group_id = ? and user_id = ?', (group_id, user_id))
        row = cursor.fetchone()
        if row:
            if len(row) > 0 and time.time() - float(row[0]) < 600:
                return True
            else:
                cursor.execute(f'update cd set lastpull = ? where group_id = ? and user_id = ?', (time.time(), group_id, user_id))
                db.commit()
                return False
        else:
            cursor.execute('insert into cd(group_id, user_id, lastpull) values (?,?,?)', (group_id, user_id, time.time()))
            db.commit()
            return False
    except Exception as e:
        print(e)
        return True
    return False

#print(do_pull({'message': 'a 18mdl1', 'keyword': 'a', 'message_type': 'group', 'group_id': 10000, 'sender':{'user_id':10000}}))
#print(pools({'message': 'a 18mdl', 'keyword': 'a', 'message_type': 'group', 'group_id': 10000, 'sender':{'user_id':10000}}))