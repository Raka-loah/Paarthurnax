import json
import os
import random
import requests
import time

new_question_keyword = '/出题'

curr = {}

questions = {}
with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\cet4.json', 'r', encoding='utf-8') as E:
    questions = json.loads(E.read())

score = {}


def new_question():
    pass


def check_answer(answer):
    pass


def get_score(user_id=0):
    # when user_id == 0 return all players' score
    pass


def generate_hint(answer):
    pass


def triviabot(j):
    # Ignore messages with no group_id
    # Double check because I'm paranoid
    if 'group_id' not in j:
        return ''

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
            question = random.sample(list(questions), k=1).pop()
            curr[j['group_id']]['question'] = '请根据音标和含义写出对应英文单词：\n{}\n{}'.format(questions[question][0], questions[question][1])
            curr[j['group_id']]['answer'] = question
            curr[j['group_id']]['time'] = time.time()
            curr[j['group_id']]['state'] = 1

        return curr[j['group_id']]['question']

    # If a question stays unanswered
    if j['group_id'] in curr and curr[j['group_id']]['state'] == 1:
        if j['message'].lower().strip() == curr[j['group_id']]['answer'].lower().strip():
            curr[j['group_id']]['state'] = 0
            return '[CQ:at,qq={}]：\n回答正确！'.format(j['sender']['user_id'])

    return ''
