# Metadata for plugin
#
# bot_command template:
# 'keyword': 
#   [function, 
#   0 - blocklist / 1 - allowlist, 
#   ['groupid1', 'groupid2'], 
#   cooldown in seconds, 
#   is message body required, 
#   is keyword regex, 
#   is suffix suppressed],

import os
import json

CR = {}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'data' ,'customReplies.json') , 'r', encoding='utf-8') as E: 
    CR = json.loads(E.read())

def custom_replies(j, resp):
    if j['message'].lower().replace(' ', '') in CR:
        resp['reply'] = CR[j['message'].lower().replace(' ', '')]
        return resp, 200
    return '', 204


Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
    },

    'preprocessors': [
    ],

    'postprocessors': [
        [custom_replies, 0, []],
    ],
}