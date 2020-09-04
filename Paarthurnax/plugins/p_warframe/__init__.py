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

import Paarthurnax.plugins.p_warframe.wfstate as wf

Metadata = {
    'alert_functions': {
        wf.get_new_alerts: '00',
        wf.get_cetus_transition: '05',
        wf.get_new_acolyte:'00',
    },

    'bot_commands': {
        '警报': [wf.get_alerts, 0, [], 0, False, False, False],
        '日常': [wf.get_challenges_daily, 0, [], 0, False, False, False],
        '周常': [wf.get_challenges_weekly, 0, [], 0, False, False, False],
        '赛季': [wf.get_challenges_season, 0, [], 0, False, False, False],
        '平原时间': [wf.get_plains_time, 0, [], 0, False, False, False],
        '每日特惠': [wf.get_dailydeal, 0, [], 0, False, False, False],
        '裂缝': [wf.get_fissures, 0, [], 0, False, False, False],
        '入侵': [wf.get_invasions, 0, [], 0, False, False, False],
        '突击': [wf.get_sorties, 0, [], 0, False, False, False],
        '奸商': [wf.get_voidtrader, 0, [], 0, False, False, False],
        '虚空商人': [wf.get_voidtrader, 0, [], 0, False, False, False],
        '帮助': [wf.get_some_help, 0, [], 0, False, False, True],
        '地球赏金': [wf.get_bounties_cetus, 0, [], 0, False, False, False],
        '金星赏金': [wf.get_bounties_solaris, 0, [], 0, False, False, False],
        '小小黑': [wf.get_acolytes, 0, [], 0, False, False, False],
        '模拟开卡': [wf.get_riven_info, 0, [], 10, True, False, False],
        '模拟突击': [wf.get_random_sortie_reward, 0, [], 0, True, False, False],
        '/wm': [wf.get_wmprice, 0, [], 10, True, False, False],
        '/mod': [wf.get_wiki_text, 0, [], 5, True, False, True],
        'wiki来': [wf.get_wiki_link, 0, [], 10, True, False, True],
        '遗物': [wf.get_relic_rewards, 0, [], 0, True, False, False],
        '出处': [wf.get_prime_part_drop_from, 0, [], 0, True, False, False],
    },

    'preprocessors': {

    },

    'postprocessors': {

    },
}