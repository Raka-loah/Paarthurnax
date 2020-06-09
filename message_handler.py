from apscheduler.schedulers.background import BackgroundScheduler
import importlib
import internal
import re
import requests
import time
import wfstate as wf
import misc
from html import unescape
from misc import msg_log

class Message_handler:
    stats = {}

    def __init__(self):
        try:
            self.cfg = importlib.import_module('config')
        except ImportError:
            self.cfg = importlib.import_module('config-sample')

        if getattr(self.cfg, 'trivia_enable', False):
            self.trivia = importlib.import_module('trivia')

        self.schduler = BackgroundScheduler()
        self.schduler.start()

    def handle(self, message):
        j = message
        C = internal.const
        cfg = self.cfg
        bot_command = cfg.bot_command

        # Response payload
        resp = {
            'reply': '',
            'at_sender': False
        }

        suffix = cfg.suffix

        if 'message' in j:
            j['message'] = unescape(j['message'])

        if 'post_type' not in j:
            return '', 204

        # QQ Requests
        if j['post_type'] == 'request':
            if (j['request_type'] == 'group' and j['sub_type'] == 'invite') or j['request_type'] == 'friend':
                resp = {
                    'approve': cfg.approve
                }
                return resp, 200

        # Logs
        log_msg = getattr(cfg, 'log_msg', True)
        if log_msg and j['post_type'] == 'message':
            if j['message_type'] == 'group':
                misc.msg_log(
                    j['message_id'],
                    j['group_id'],
                    j['sender']['user_id'],
                    j['message'])
            else:
                misc.msg_log(
                    j['message_id'],
                    '0',
                    j['sender']['user_id'],
                    j['message'])

        # All queries from banned senders and bot themselves are directly
        # dropped
        banned_sender = cfg.banned_sender
        if j['sender']['user_id'] == j['self_id'] or j['sender']['user_id'] in banned_sender:
            return '', 204

        # CQ tag for @sender if message type is group
        title = ''
        if hasattr(cfg, 'custom_title') and j['message_type'] == 'group':
            if j['sender']['user_id'] in cfg.custom_title:
                if j['group_id'] in cfg.custom_title[j['sender']['user_id']]:
                    title = cfg.custom_title[j['sender']['user_id']][j['group_id']]
                elif 'default' in cfg.custom_title[j['sender']['user_id']]:
                    title = cfg.custom_title[j['sender']['user_id']]['default']
            elif 'default' in cfg.custom_title:
                title = cfg.custom_title['default']

        at_sender = f"{title}[CQ:at,qq={j['sender']['user_id']}]：\n" if j['message_type'] == 'group' else ''

        # Determine which keyword got called
        matched_keyword = None
        for keyword, function in self.cfg.bot_command.items():
            # Is it a regex?
            if function[5] == C.REGEX:
                match = re.match(keyword, j['message'])
                if match:
                    matched_keyword = keyword
                    break
            # Is it a full match?
            elif function[4] == C.NO_MSG:
                if j['message'] == keyword:
                    matched_keyword = keyword
                    break
            # Is it a partial match?
            elif j['message'].startswith(keyword):
                matched_keyword = keyword
                break
        
        # Check filter
        if matched_keyword is not None:
            if j['message_type'] == 'group':
                if bot_command[matched_keyword][1] == C.BLOCKLIST:
                    if j['group_id'] in bot_command[matched_keyword][2]:
                        matched_keyword = None
                else:
                    if j['group_id'] not in bot_command[matched_keyword][2]:
                        matched_keyword = None

        # If we got a keyword
        if matched_keyword is not None:
            # Check cooldown
            if matched_keyword in self.stats:
                if time.time() - self.stats[matched_keyword] < bot_command[matched_keyword][3]:
                    resp['reply'] = at_sender + internal.cooldown()
                    return resp, 200
                else:
                    self.stats[matched_keyword] = time.time()
            else:
                self.stats[matched_keyword] = time.time()

            # Handle command
            j['keyword'] = matched_keyword
            try:
                if bot_command[matched_keyword][4] == C.NO_MSG:
                    msg = bot_command[matched_keyword][0]()
                else:
                    msg = bot_command[matched_keyword][0](j)
            except BaseException:
                msg = ''

            if msg != '':
                # Is keyword suppressed?
                if bot_command[matched_keyword][6] == C.SUPPRESSED:
                    resp['reply'] = msg
                elif bot_command[matched_keyword][4] == C.NO_MSG:
                    resp['reply'] = msg + suffix
                else:
                    resp['reply'] = at_sender + msg
                return resp, 200

        # Custom replies
        if j['message'].lower().replace(' ', '') in wf.data_dict['CR']:
            resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ', '')]
            return resp, 200

        # Autoban
        try:
            if j['message_type'] == 'group':
                ban_word = cfg.ban_word
                for word in ban_word:
                    if word in j['message'].replace(' ', ''):
                        resp['ban'] = True
                        resp['ban_duration'] = cfg.ban_duration
                        return resp, 200
        except BaseException:
            pass

        # Trivia
        try:
            trivia_enable = getattr(cfg, 'trivia_enable', False)
            if j['message_type'] == 'group' and trivia_enable:
                resp['reply'] = self.trivia.triviabot(j)
                if resp['reply'] != '':
                    return resp, 200
        except BaseException:
            pass

        try:
            if j['message'].lower().strip() == trivia.curr[j['group_id']]['answer'].lower().strip():
                return '', 204
        except BaseException:
            pass

        # "Execute" person nobody cared about within 120 seconds
        # The Nature of Humanity, will override Execution
        # cfg.noh_whitelist is deprecated and this is purely for backwards-compatibility
        # and will be removed in the near future
        noh_allowlist = getattr(cfg, 'noh_allowlist', getattr(cfg, 'noh_whitelist', []))
        if j['message_type'] == 'group':
            resp['reply'] = misc.msg_executioner(j) 
            if resp['reply'] == '' and j['group_id'] in noh_allowlist:
                resp['reply'] = misc.msg_nature_of_humanity(j)

        if resp['reply'] != '':
            return resp, 200
        else:
            return '', 204

    def add_job(self, broadcast_func, second='00'):
        if getattr(self.cfg, 'enable_broadcast', False):
            self.schduler.add_job(self.send_broadcast, 'cron', second=second, args=[broadcast_func])

    def send_broadcast(self, broadcast_func):
        broadcast_group = self.cfg.broadcast_group
        msg = broadcast_func()
        if msg != '':
            url = f"{getattr(self.cfg, 'base_url', 'http://127.0.0.1:5700')}/send_group_msg_async"
            for group_id in broadcast_group:
                payload = {
                    'group_id': group_id,
                    'message': msg
                }
                requests.post(url, json=payload)

    def reload(self, request_token):
        access_token = getattr(self.cfg, 'reload_token', '')  # Access Token

        if request_token == access_token and access_token != '':
            importlib.reload(wf)
            importlib.reload(misc)
            return 'Successfully reloaded modules.', 200
        else:
            return 'Access Denied.', 403

