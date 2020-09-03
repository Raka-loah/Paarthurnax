# -*- coding: utf-8 -*-

import random

def cooldown():
    replies = ['我还不能施放这个法术', '这个法术还在冷却中', '法术冷却中', '我还没准备好施放这个法术', '被抵抗，请稍后再试']
    return random.choice(replies)