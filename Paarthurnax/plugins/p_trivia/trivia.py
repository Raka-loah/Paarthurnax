import importlib
import json
import os
import random
import requests
from datetime import datetime, timedelta
from Paarthurnax.plugins.p_trivia.trivia_plugins.chinese_idioms.game import idioms_game
from apscheduler.schedulers.background import BackgroundScheduler

new_question_keyword = '/出题'
time_limit_seconds = 120
routine_cleanup_hours = 2

# For most of the time this should be true now
image_perm = True

curr = {}

#from trivia_plugins.cet4.game import cet4_game
#game = cet4_game()

game = idioms_game()
game.clean()

def triviabot(j, resp):
    # Ignore messages with no group_id
    # Double check because I'm paranoid
    if 'group_id' not in j:
        return '', 204

    if game.require_image and (image_perm != True):
        return '', 204

    # Someone wanted a new question
    if j['message'] == new_question_keyword:
        # Initialize dict
        if j['group_id'] not in curr:
            curr[j['group_id']] = {
                'state': 0
            }

        # Send a new question if state 0
        # Send old question if else
        if curr[j['group_id']]['state'] == 0:
            res = game.generate(j['group_id'])
            curr[j['group_id']]['question'] = res['question']
            curr[j['group_id']]['answer'] = res['answer']
            print(f'群{j["group_id"]}答案：{res["answer"]}')
            curr[j['group_id']]['answer_announce'] = res['answer_announce']
            curr[j['group_id']]['hint'] = res['hint']
            curr[j['group_id']]['time'] = datetime.now()
            curr[j['group_id']]['state'] = 1
            curr[j['group_id']]['job'] = scheduler.add_job(time_up, 'date', run_date=curr[j['group_id']]['time'] + timedelta(seconds=time_limit_seconds), args=[j['group_id'], curr[j['group_id']]['answer']])
            curr[j['group_id']]['job_hint'] = scheduler.add_job(hint, 'date', run_date=curr[j['group_id']]['time'] + timedelta(seconds=time_limit_seconds/2), args=[j['group_id'], curr[j['group_id']]['hint']])

        resp['reply'] = f"{curr[j['group_id']]['question']}\n剩余时间：{time_limit_seconds - (datetime.now() - curr[j['group_id']]['time']).total_seconds():.0f}秒"

        return resp, 200

    # If a question stays unanswered
    if j['group_id'] in curr and curr[j['group_id']]['state'] == 1:
        if j['message'].lower().strip() == curr[j['group_id']]['answer'].lower().strip():
            curr[j['group_id']]['state'] = 0
            try:
                curr[j['group_id']]['job'].remove()
            except:
                pass
            try:
                curr[j['group_id']]['job_hint'].remove()
            except:
                pass
            resp['reply'] = f"[CQ:at,qq={j['sender']['user_id']}]{curr[j['group_id']]['answer_announce']}"
            return resp, 200

    return '', 204

def time_up(group_id, answer):
    url = f"{j['base_url']}/send_group_msg_async"
    payload = {
        'group_id': group_id,
        'message': f'时间到，无人答对，正确答案是：{answer}'
    }
    requests.post(url, json=payload)
    curr[group_id]['state'] = 0

def hint(group_id, hint):
    if len(hint) > 0:
        url = f"{j['base_url']}/send_group_msg_async"
        payload = {
            'group_id': group_id,
            'message': f'时间过半！\n{hint}'
        }
        requests.post(url, json=payload)

def routine_clean():
    game.clean()

scheduler = BackgroundScheduler()
scheduler.add_job(routine_clean, 'interval', hours=routine_cleanup_hours)
scheduler.start()