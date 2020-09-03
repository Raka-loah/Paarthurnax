# Base URL for Onebot API endpoints
base_url = 'http://127.0.0.1:5700'


# Suffix for C.NO_MSG commands
suffix = '\n更多命令请输入"帮助"。'

# Approve group and friend invites
approve = True

# Banned senders
banned_sender = []

# Broadcast
enable_broadcast = False
broadcast_group = []

# Access token for server quick reload
reload_token = ''

# Custom user titles
# Titles that appear before a '@' tag
#
# Template:
# custom_title = {
#     'default': '',
#     user_id: {
#         'default': '',
#         group_id: '',
#     }
# }
#
# Parameters(all optional):
# 'default': Default title for everyone
# user_id: Titles would be assigned to this user
# user_id -> group_id: Specific title in specific group for user
# user_id -> 'default': Default title for this user
#
# If you want to assign titles to many, many users, 
# use a loop to modify this dictionary on the go.

custom_title = {
    'default': '',
    10000: {
        'default': '',
        10000: '',
    }
}