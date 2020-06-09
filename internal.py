# -*- coding: utf-8 -*-

from collections import namedtuple
import random

# C.BLACKLIST and C.WHITELIST are now deprecated.
# Use C.BLOCKLIST and C.ALLOWLIST instead.
constants = namedtuple('Constants', ['MSG', 'NO_MSG', 'REGEX', 'NOT_REGEX', 'SUPPRESSED', 'NOT_SUPPRESSED', 'BLACKLIST', 'WHITELIST', 'BLOCKLIST', 'ALLOWLIST'])
const = constants(True, False, True, False, True, False, 0, 1, 0, 1)

def cooldown():
    replies = ['我还不能施放这个法术', '这个法术还在冷却中', '法术冷却中', '我还没准备好施放这个法术', '被抵抗，请稍后再试']
    return random.choice(replies)