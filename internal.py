# -*- coding: utf-8 -*-

from collections import namedtuple
import random
import wfstate as wf
import misc

# C.BLACKLIST and C.WHITELIST are now deprecated.
# Use C.BLOCKLIST and C.ALLOWLIST instead.
constants = namedtuple('Constants', ['MSG', 'NO_MSG', 'REGEX', 'NOT_REGEX', 'SUPPRESSED', 'NOT_SUPPRESSED', 'BLACKLIST', 'WHITELIST', 'BLOCKLIST', 'ALLOWLIST'])
const = constants(True, False, True, False, True, False, 0, 1, 0, 1)
C = const

def cooldown():
    replies = ['我还不能施放这个法术', '这个法术还在冷却中', '法术冷却中', '我还没准备好施放这个法术', '被抵抗，请稍后再试']
    return random.choice(replies)


bot_command_default = {
    'wf.get_alerts': [True, '警报', wf.get_alerts, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_challenges_daily': [True, '日常', wf.get_challenges_daily, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_challenges_weekly': [True, '周常', wf.get_challenges_weekly, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_challenges_season': [True, '赛季', wf.get_challenges_season, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_plains_time': [True, '平原时间', wf.get_plains_time, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_dailydeal': [True, '每日特惠', wf.get_dailydeal, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_fissures': [True, '裂缝', wf.get_fissures, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_invasions': [True, '入侵', wf.get_invasions, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_sorties': [True, '突击', wf.get_sorties, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_voidtrader': [True, '奸商', wf.get_voidtrader, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_voidtrader': [True, '虚空商人', wf.get_voidtrader, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_some_help': [True, '帮助', wf.get_some_help, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    'wf.get_bounties_cetus': [True, '地球赏金', wf.get_bounties_cetus, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_bounties_solaris': [True, '金星赏金', wf.get_bounties_solaris, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.general': [True, '吃什么', misc.general, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.breakfast': [True, '早饭吃什么', misc.breakfast, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.lunch': [True, '午饭吃什么', misc.lunch, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.dinner': [True, '晚饭吃什么', misc.dinner, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.SUPPRESSED],
    'wf.get_acolytes': [True, '小小黑', wf.get_acolytes, C.BLOCKLIST, [], 0, C.NO_MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_riven_info': [True, '模拟开卡', wf.get_riven_info, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_random_sortie_reward': [True, '模拟突击', wf.get_random_sortie_reward, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_wmprice': [True, '/wm', wf.get_wmprice, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_wiki_text': [True, '/mod', wf.get_wiki_text, C.BLOCKLIST, [], 5, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.ask_8ball': [True, '/ask', misc.ask_8ball, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.misc_roll': [True, '/roll', misc.misc_roll, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_ar_wrapper': [True, '/echo', misc.msg_ar_wrapper, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.msg_ar_wrapper': [True, '/stalk', misc.msg_ar_wrapper, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.let_me_baidu_that_for_you': [True, '/百度', misc.let_me_baidu_that_for_you, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.music_share': [True, '点歌', misc.music_share, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.music_share': [True, '来首', misc.music_share, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.draw_tarot': [True, '/tarot', misc.draw_tarot, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_wiki_link': [True, 'wiki来', wf.get_wiki_link, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.SUPPRESSED],
    'misc.msg_translate_bing': [True, '/翻译', misc.msg_translate_bing, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_demotivational': [True, 'hurt me', misc.msg_demotivational, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_tackypickuplines': [True, 'tease me', misc.msg_tackypickuplines, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.russian_roulette': [True, '/rr', misc.russian_roulette, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_stella': [False, '/stella', misc.msg_stella, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_bankrupt': [True, r'.*今天.+了吗', misc.msg_bankrupt, C.BLOCKLIST, [], 0, C.MSG, C.REGEX, C.NOT_SUPPRESSED],
    'misc.msg_aqi': [True, '/aqi', misc.msg_aqi, C.BLOCKLIST, [], 5, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'misc.msg_exchange_rate': [True, '/汇率', misc.msg_exchange_rate, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_riven_prices': [True, '/紫卡', wf.get_riven_prices, C.BLOCKLIST, [], 10, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_relic_rewards': [True, '遗物', wf.get_relic_rewards, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
    'wf.get_prime_part_drop_from': [True, '出处', wf.get_prime_part_drop_from, C.BLOCKLIST, [], 0, C.MSG, C.NOT_REGEX, C.NOT_SUPPRESSED],
}