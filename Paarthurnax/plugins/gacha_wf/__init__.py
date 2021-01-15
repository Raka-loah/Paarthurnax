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

from Paarthurnax.plugins.gacha_wf.gacha import do_pull

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
        '抽卡': [do_pull, 0, [], 0, True, False, False],
    },

    'preprocessors': [
    ],

    'postprocessors': [
    ],
}