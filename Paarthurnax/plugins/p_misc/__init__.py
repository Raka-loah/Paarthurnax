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

import Paarthurnax.plugins.p_misc.misc as misc

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
        '吃什么': [misc.general, 0, [], 0, False, False, True],
        '早饭吃什么': [misc.breakfast, 0, [], 0, False, False, True],
        '午饭吃什么': [misc.lunch, 0, [], 0, False, False, True],
        '晚饭吃什么': [misc.dinner, 0, [], 0, False, False, True],
        '/ask': [misc.ask_8ball, 0, [], 0, True, False, False],
        '/roll': [misc.misc_roll, 0, [], 0, True, False, False],
        '/stalk': [misc.msg_ar_wrapper, 0, [], 0, True, False, True],
        '/百度': [misc.let_me_baidu_that_for_you, 0, [], 10, True, False, True],
        '点歌': [misc.music_share, 0, [], 0, True, False, True],
        '来首': [misc.music_share, 0, [], 0, True, False, True],
        '/tarot': [misc.draw_tarot, 0, [], 10, True, False, False],
        '/翻译': [misc.msg_translate_bing, 0, [], 10, True, False, False],
        'hurt me': [misc.msg_demotivational, 0, [], 0, True, False, False],
        'tease me': [misc.msg_tackypickuplines, 0, [], 0, True, False, False],
        '/rr': [misc.russian_roulette, 0, [], 0, True, False, False],
        # '/stella': [misc.msg_stella, 0, [], 0, True, False, False],
        r'.*今天.+了吗': [misc.msg_bankrupt, 0, [], 0, True, True, False],
        '/aqi': [misc.msg_aqi, 0, [], 5, True, False, False],
        '/汇率': [misc.msg_exchange_rate, 0, [], 0, True, False, False],
    },

    'preprocessors': [
    ],

    'postprocessors': [
        [misc.msg_nature_of_humanity, 1, []],
        [misc.msg_executioner, 1, []],
    ],
}