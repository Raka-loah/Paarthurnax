import json
import os
import random
import sqlite3
import time

card_pool = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'data' ,'card.json') , 'r', encoding='utf-8') as E:
    card_pool = json.loads(E.read())

rates = {
    'SSR': card_pool['settings']['rates']['SSR'],
    'UR': card_pool['settings']['rates']['UR'],
    'LR': card_pool['settings']['rates']['LR'],
    'R': (1 - card_pool['settings']['rates']['SSR'] - card_pool['settings']['rates']['UR'] - card_pool['settings']['rates']['LR']) * 0.8,
    'SR': (1 - card_pool['settings']['rates']['SSR'] - card_pool['settings']['rates']['UR'] - card_pool['settings']['rates']['LR']) * 0.2,
}

def do_pull(j):
    if j['message_type'] != 'group':
        return '抱歉，抽卡仅限指定QQ群内使用。'

    if cd(j['group_id'], j['sender']['user_id']):
        return '距离上次抽卡不足10分钟，指挥官请耐心等候。'

    if card_pool['settings']['guarantee_last']:
        pull = random.choices([x for x in rates.keys()], weights=[float(x) for x in rates.values()], k=9)
        guarantee = random.choices(card_pool['settings']['guarantee_rarity'], weights=[float(rates[x]) for x in card_pool['settings']['guarantee_rarity']], k=1)
        pull.extend(guarantee)
    else:
        pull = random.choices([x for x in rates.keys()], weights=[float(x) for x in rates.values()], k=10)
    
    rare_cards = []
    for card in pull:
        if card in ['SSR', 'UR', 'LR']:
            rare_cards.append([card, random.choice(card_pool['cards'][card])])

    message = f'十连抽出了：\n'
    for card in rare_cards:
        message += f'[{card_pool["settings"][card[0]]}]！{card[1][0]}\n“{card[1][1]}”\n\n'
    if len(rare_cards) == 0:
        message += '只有R和SR……'

    return message.strip()

def connect():
    try:
        db = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'cd.sqlite'))
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