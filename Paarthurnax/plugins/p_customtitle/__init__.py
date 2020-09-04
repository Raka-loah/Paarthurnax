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


custom_titles = {
    'default': '',
    'personal': {
        416939937: '大蜥蜴',
    },
    209396470: {
        'default': '',
        416939937: '创始人',
    },
}

def custom_title(j):
    title = ''
    if custom_titles and j['message_type'] == 'group':
        if j['group_id'] in custom_titles:
            if j['sender']['user_id'] in custom_titles[j['group_id']]:
                title = custom_titles[j['group_id']][j['sender']['user_id']]
            elif 'default' in custom_titles[j['group_id']]:
                title = custom_titles[j['group_id']]['default']
        elif j['sender']['user_id'] in custom_titles['personal']:
            title = custom_titles['personal'][j['sender']['user_id']]
        elif 'default' in custom_titles:
            title = custom_titles['default']
    j['at_sender'] = f"{title}{j['at_sender']}"

    return j, False

Metadata = {
    'alert_functions': {
    },

    'bot_commands': {
    },

    'preprocessors': [
        [custom_title, 0, []],
    ],

    'postprocessors': [
    ],
}