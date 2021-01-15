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

from Paarthurnax.plugins.gacha_fgo.gacha import do_pull, pools

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
        '十连': [do_pull, 0, [], 0, True, False, True],
        '卡池': [pools, 0, [], 0, False, False, True],
    },

    'preprocessors': [
    ],

    'postprocessors': [
    ],
}