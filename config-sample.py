# Usage: Copy this file and rename it to config.py
# Then modify the new config.py

import internal
import misc
import trivia
import wfstate as wf

C = internal.const

# Command Template:
# 'keyword': [function, fliter_type, [group_ids], cool_down, message, is_regex, is_suppressed]
#
# Parameters:
# function: Callback function
# filter_type: 0 - Blacklist, only specific groups banned from this keyword
#              1 - Whitelist, only specific groups can use this keyword, duh.
# [group_ids]: Group ids for the filter
# cool_down: Cool down of this keyword in seconds, shared between all groups
# message: True - Callback function will get POSTed message as argument
#          False - Just call that function maybe
# is_regex: True - This keyword is a regular expression
#           False - This keyword is NOT a regular expression
# is_suppressed: True - Do not append suffix or @sender tag
#                False - Append suffix or @sender tag

bot_command = {
    '警报': [wf.get_alerts, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '日常': [wf.get_challenges_daily, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '周常': [wf.get_challenges_weekly, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '赛季': [wf.get_challenges_season, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '平原时间': [wf.get_plains_time, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '每日特惠': [wf.get_dailydeal, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '裂缝': [wf.get_fissures, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '入侵': [wf.get_invasions, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '突击': [wf.get_sorties, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '奸商': [wf.get_voidtrader, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '虚空商人': [wf.get_voidtrader, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '帮助': [wf.get_some_help, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '地球赏金': [wf.get_bounties_cetus, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '金星赏金': [wf.get_bounties_solaris, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '吃什么': [misc.general, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '早饭吃什么': [misc.breakfast, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '午饭吃什么': [misc.lunch, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '晚饭吃什么': [misc.dinner, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    '小小黑': [wf.get_acolytes, C.BLACKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '模拟开卡': [wf.get_riven_info, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '模拟突击': [wf.get_random_sortie_reward, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/wm': [wf.get_wmprice, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/mod': [wf.get_wiki_text, C.BLACKLIST, [], 5, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/ask': [misc.ask_8ball, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/roll': [misc.misc_roll, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/echo': [misc.msg_ar_wrapper, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/stalk': [misc.msg_ar_wrapper, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/百度': [misc.let_me_baidu_that_for_you, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '点歌': [misc.music_share, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '来首': [misc.music_share, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/tarot': [misc.draw_tarot, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wiki来': [wf.get_wiki_link, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    '/翻译': [misc.msg_translate_bing, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'hurt me': [misc.msg_demotivational, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'tease me': [misc.msg_tackypickuplines, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/rr': [misc.russian_roulette, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    # '/stella': [misc.msg_stella, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    r'.*今天.+了吗': [misc.msg_bankrupt, C.BLACKLIST, [], 0, C.MSG, C.REGEX, C.NOT_SUPPRESSED],
    '/aqi': [misc.msg_aqi, C.BLACKLIST, [], 5, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/汇率': [misc.msg_exchange_rate, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '/紫卡': [wf.get_riven_prices, C.BLACKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '遗物': [wf.get_relic_rewards, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    '出处': [wf.get_prime_part_drop_from, C.BLACKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
}

# Suffix for C.NO_MSG commands
suffix = '\n更多命令请输入"帮助"。'

# Approve group and friend invites
approve = True

# Banned senders
banned_sender = ['']

# Broadcast
enable_broadcast = True
broadcast_group = [697991343]

# Auto ban
# Example: ban_word = ['foo', 'bar']
# Ban duration in seconds, defualt: 300
ban_word = []
ban_duration = 300

# Access token for server quick reload
reload_token = ''