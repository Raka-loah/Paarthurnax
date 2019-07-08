import re
import requests
import requests_cache


legends_names = {
    'wraith': '恶灵',
    'bloodhound': '寻血猎犬',
    'bangalore': '班加罗尔',
    'lifeline': '命脉',
    'gibraltar': '直布罗陀',
    'pathfinder': '探路者',
    'mirage': '幻象',
    'caustic': '侵蚀',
}


legends_stats = {
    'revives': '复活队友的次数',
    'kills': '击杀',
}


def msg_get_user_stats(j):
    """Get APEX Legends user stats.
    
    Returns a string I guess?
    """
    msg = ''

    match = re.match(r'.*? (.*?) (.*?)', j['message'])

    if match:
        platform = match.group(2)
        name = match.group(1)
    else:
        return ''

    appkey = '' # Your APP key

    url = 'https://www.apexlegendsapi.com/api/v1/player?platform={}&name={}'.format(platform, name)
    headers = {
        'Authorization': appkey
    }
    tracks = '追踪数据：'
    try:
        r = requests_cache.CachedSession(cache_name='apex', backend='memory', expire='300')
        stats = r.get(url, headers=headers, timeout=30).json()
        for stat in stats['legends'][0]['stats']:
            for stat_name, stat_value in stat.items():
                stat_name = legends_stats[stat_name] if stat_name in legends_stats else stat_name
                tracks += '\n{}：{}'.format(stat_name, stat_value)
        msg = 'ID：{} ({}) 等级：{}\n上一场使用：{}\n{}'.format(stats['name'], stats['platform'].upper(), stats['level'], legends_names[stats['legends'][0]['name']], tracks)
    except BaseException:
        msg = '[ERROR]无法连接到APEX英雄API。'
    return msg