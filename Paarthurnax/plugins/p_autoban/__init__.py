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

ban_duration = 300

def autoban(j, resp):
    try:
        if j['message_type'] == 'group':
            ban_word = []
            for word in ban_word:
                if word in j['message'].replace(' ', ''):
                    resp['ban'] = True
                    resp['ban_duration'] = ban_duration
                    return resp, 200
    except BaseException:
        pass

    return '', 204

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
    },

    'preprocessors': [
    ],

    'postprocessors': [
        [autoban, 0, []],
    ],
}