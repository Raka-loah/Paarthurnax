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

import Paarthurnax.plugins.p_trivia.trivia as trivia

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
    },

    'preprocessors': [
    ],

    'postprocessors': [
        [trivia.triviabot, 0, []],
    ],
}