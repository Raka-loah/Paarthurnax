from apscheduler.schedulers.background import BackgroundScheduler
import importlib
import consts as internal
import re
import requests
import time
import os
import json
from html import unescape

class Talking_Dragon:
    """
    Spawn a new instance of Paarthurnax.

    Let him hear what you say.
    """

    def __init__(self):
        try:
            cfg = importlib.import_module('config')
            self.__cfg = cfg
        except:
            try:
                cfg = importlib.import_module('config-sample')
                self.__cfg = cfg
            except:
                raise ValueError('[Crush landing] Can not read config.py!')

        self.__botcommand = {}
        self.__stats = {}
        self.__alerts = {}
        self.__preprocessors = []
        self.__postprocessors = []

        plugins = [ f.name for f in os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'plugins')) if f.is_dir() ]

        for plugin in plugins:
            try:
                module = importlib.import_module(f'plugins.{plugin}')
                metadata = module.Metadata
                if 'alert_functions' in metadata:
                    self.__alerts.update(metadata['alert_functions'])
                if 'bot_commands' in metadata:
                    self.__botcommand.update(metadata['bot_commands'])
                if 'preprocessors' in metadata:
                    self.__preprocessors.extend(metadata['preprocessors']) 
                if 'postprocessors' in metadata:
                    self.__postprocessors.extend(metadata['postprocessors']) 
            except Exception as e:
                print(f'Module {plugin} has no metadata, skipped.')

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings', 'settings.json'), 'r', encoding='utf-8') as f:
                settings = json.load(f)
            new_command = {}
            for command in self.__botcommand.keys():
                func_name = f'{self.__botcommand[command][0].__module__}.{self.__botcommand[command][0].__name__}'
                if func_name in settings:
                    func = self.__botcommand[command][0]
                    new_command[settings[func_name][0]] = [func] + settings[func_name][1:]
                else:
                    new_command[command] = self.__botcommand[command]
            self.__botcommand = new_command
        except Exception as e:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings', 'settings.json'), 'w+', encoding='utf-8') as f:
                settings = {}
                for command in self.__botcommand.keys():
                    settings[f'{self.__botcommand[command][0].__module__}.{self.__botcommand[command][0].__name__}'] = [command] + self.__botcommand[command][1:]
                f.write(json.dumps(settings, ensure_ascii=False))

        self.__schduler = BackgroundScheduler()
        self.__schduler.start()
        for func in self.__alerts.keys():
            self.__add_job(func, self.__alerts[func])

    def __log(self, message_id, group_id, sender_id, message):
        try:
            db = sqlite3.connect('qqbot.sqlite')
            cursor = db.cursor()
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS messages(id INTEGER, group_id INTEGER, sender_id INTEGER, message TEXT, timestamp REAL)''')
            db.commit()
        except BaseException:
            db.rollback()
            db.close()
            return '[ERROR] Database error'

        try:
            cursor.execute(
                '''INSERT INTO messages(id, group_id, sender_id, message, timestamp) VALUES(?, ?, ?, ?, ?)''',
                (message_id,
                group_id,
                sender_id,
                message,
                time.time()))
            db.commit()
        except BaseException:
            db.rollback()
        finally:
            db.close()
            return '[INFO] Transaction complete'

    def hear(self, message):
        j = message
        C = internal.const
        cfg = self.__cfg
        bot_command = cfg.get('bot_command')

        # Initialize Response payload
        resp = {
            'reply': '',
            'at_sender': False
        }

        # Help text
        suffix = cfg.get('suffix')

        # Unescape message
        if 'message' in j:
            j['message'] = unescape(j['message'])

        # Return 204 if not a valid message
        if 'post_type' not in j:
            return '', 204

        # Friend/Group Requests
        if j['post_type'] == 'request':
            if (j['request_type'] == 'group' and j['sub_type'] == 'invite') or j['request_type'] == 'friend':
                resp = {
                    'approve': cfg.get('approve')
                }
                return resp, 200

        # Do not process self-sent messages
        banned_sender = cfg.get('banned_sender')
        if j['sender']['user_id'] == j['self_id'] or j['sender']['user_id'] in banned_sender:
            return '', 204

        # Logs
        log_msg = cfg.get('log_msg', True)
        if log_msg and j['post_type'] == 'message':
            if j['message_type'] == 'group':
                self.__log(
                    j['message_id'],
                    j['group_id'],
                    j['sender']['user_id'],
                    j['message'])
            else:
                self.__log(
                    j['message_id'],
                    '0',
                    j['sender']['user_id'],
                    j['message'])

        # CQ tag for @sender if message type is group
        title = ''
        if cfg.get('custom_title', None) and j['message_type'] == 'group':
            if j['sender']['user_id'] in cfg.get('custom_title'):
                if j['group_id'] in cfg.get('custom_title')[j['sender']['user_id']]:
                    title = cfg.get('custom_title')[j['sender']['user_id']][j['group_id']]
                elif 'default' in cfg.get('custom_title')[j['sender']['user_id']]:
                    title = cfg.get('custom_title')[j['sender']['user_id']]['default']
            elif 'default' in cfg.get('custom_title'):
                title = cfg.get('custom_title')['default']

        at_sender = f"{title}[CQ:at,qq={j['sender']['user_id']}]：\n" if j['message_type'] == 'group' else ''

        # Preprocessors
        for func in self.__preprocessors:
            j = func(j)

        # If some preprocessor went wrong
        if 'message' not in j:
            return '', 204

        # Determine which keyword got called
        matched_keyword = None
        for keyword, function in bot_command.items():
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
            if matched_keyword in self.__stats:
                if time.time() - self.__stats[matched_keyword] < bot_command[matched_keyword][3]:
                    resp['reply'] = at_sender + internal.cooldown()
                    return resp, 200
                else:
                    self.__stats[matched_keyword] = time.time()
            else:
                self.__stats[matched_keyword] = time.time()

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

        # # Custom replies
        # if j['message'].lower().replace(' ', '') in wf.data_dict['CR']:
        #     resp['reply'] = wf.data_dict['CR'][j['message'].lower().replace(' ', '')]
        #     return resp, 200

        # Postprocessors
        status_code = 204
        for func in self.__postprocessors:
            resp, status_code = func(j, resp, status_code)

        # # Autoban
        # try:
        #     if j['message_type'] == 'group':
        #         ban_word = cfg.get('ban_word')
        #         for word in ban_word:
        #             if word in j['message'].replace(' ', ''):
        #                 resp['ban'] = True
        #                 resp['ban_duration'] = cfg.get('ban_duration')
        #                 return resp, 200
        # except BaseException:
        #     pass

        # # Trivia
        # try:
        #     trivia_enable = cfg.get('trivia_enable', False)
        #     if j['message_type'] == 'group' and trivia_enable:
        #         resp['reply'] = self.trivia.triviabot(j)
        #         if resp['reply'] != '':
        #             return resp, 200
        # except BaseException:
        #     pass

        # try:
        #     if j['message'].lower().strip() == trivia.curr[j['group_id']]['answer'].lower().strip():
        #         return '', 204
        # except BaseException:
        #     pass

        # # "Execute" person nobody cared about within 120 seconds
        # # The Nature of Humanity, will override Execution
        # # cfg.noh_whitelist is deprecated and this is purely for backwards-compatibility
        # # and will be removed in the near future
        # noh_allowlist = cfg.get('noh_allowlist', cfg.get('noh_whitelist', []))
        # if j['message_type'] == 'group':
        #     resp['reply'] = misc.msg_executioner(j) 
        #     if resp['reply'] == '' and j['group_id'] in noh_allowlist:
        #         resp['reply'] = misc.msg_nature_of_humanity(j)

        if resp['reply'] != '':
            return resp, status_code
        else:
            return '', status_code

    def __add_job(self, broadcast_func, second='00'):
        if hasattr(self.__cfg, 'enable_broadcast') and self.__cfg.enable_broadcast:
            self.__schduler.add_job(self.__send_broadcast, 'cron', second=second, args=[broadcast_func])

    def __send_broadcast(self, broadcast_func):
        broadcast_group = self.__cfg.broadcast_group
        msg = broadcast_func()
        if msg != '':
            url = f"{self.__cfg.get('base_url', 'http://127.0.0.1:5700')}/send_group_msg_async"
            for group_id in broadcast_group:
                payload = {
                    'group_id': group_id,
                    'message': msg
                }
                requests.post(url, json=payload)

    def reload(self, request_token):
        access_token = self.__cfg.get('reload_token', '')  # Access Token

        if request_token == access_token and access_token != '':
            importlib.reload(wf)
            importlib.reload(misc)
            return 'Successfully reloaded modules.', 200
        else:
            return 'Access Denied.', 403

