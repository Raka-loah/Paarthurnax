from apscheduler.schedulers.background import BackgroundScheduler
import importlib
import Paarthurnax.consts as internal
import re
import requests
import time
import os
import json
from html import unescape
import sqlite3

class Talking_Dragon:
    """
    Spawn a new instance of Paarthurnax.

    It can hear, study, take and check.
    """

    def __init__(self):
        try:
            cfg = importlib.import_module('Paarthurnax.config')
            self.__cfg = cfg
        except:
            try:
                cfg = importlib.import_module('Paarthurnax.config-sample')
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
                module = importlib.import_module(f'Paarthurnax.plugins.{plugin}')
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
                print(f'Module {plugin}: {e}.')

        self.study()

        self.__schduler = BackgroundScheduler()
        self.__schduler.start()
        for func in self.__alerts.keys():
            if self.__alerts[func][1]:
                self.__add_job(func, self.__alerts[func][0])

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

    def hear(self, Onebot_message_json):
        """
        The dragon will now heed those mere mortals and speak its wisdom when necessary.

        Translate: Process Onebot message json, then return reply and status_code.
        """
        j = Onebot_message_json
        cfg = self.__cfg
        bot_command = self.__botcommand

        # Initialize Response payload
        resp = {
            'reply': '',
            'at_sender': False
        }

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
                    'approve': getattr(cfg, 'approve', False)
                }
                return resp, 200

        # Do not process self-sent messages
        banned_sender = getattr(cfg, 'banned_sender', [])
        if j['sender']['user_id'] == j['self_id'] or j['sender']['user_id'] in banned_sender:
            return '', 204

        j['at_sender'] = f"[CQ:at,qq={j['sender']['user_id']}]：\n" if j['message_type'] == 'group' else ''

        j['base_url'] = getattr(cfg, 'base_url', 'http://127.0.0.1:5700')

        j['suffix'] = getattr(cfg, 'suffix', '')

        j['query'] = self.query

        j['api'] = self.api

        # Preprocessors
        for func in self.__preprocessors:
            if func[1] == 0 and j['group_id'] in [int(x) for x in func[2] if x != '']:
                continue
            elif func[1] == 1 and j['group_id'] not in [int(x) for x in func[2] if x != '']:
                continue
            j, halt = func[0](j)
            if halt:
                return '', 204

        # Logs
        log_msg = getattr(cfg, 'log_msg', True)
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

        # If some preprocessor went wrong
        if 'message' not in j:
            return '', 204

        # Determine which keyword got called
        matched_keyword = None
        for keyword, function in bot_command.items():
            # Is this function Enabled?
            if not function[7]:
                break
            # Is it a regex?
            if function[5] == True:
                match = re.match(keyword, j['message'])
                if match:
                    matched_keyword = keyword
                    break
            # Is it a full match?
            elif function[4] == False:
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
                if bot_command[matched_keyword][1] == 0:
                    if j['group_id'] in [int(x) for x in bot_command[matched_keyword][2] if x != '']:
                        matched_keyword = None
                else:
                    if j['group_id'] not in [int(x) for x in bot_command[matched_keyword][2] if x != '']:
                        matched_keyword = None

        # If we got a keyword
        if matched_keyword is not None:
            # Check cooldown
            if matched_keyword in self.__stats:
                if time.time() - self.__stats[matched_keyword] < bot_command[matched_keyword][3]:
                    resp['reply'] = j['at_sender'] + internal.cooldown()
                    return resp, 200
                else:
                    self.__stats[matched_keyword] = time.time()
            else:
                self.__stats[matched_keyword] = time.time()

            # Handle command
            j['keyword'] = matched_keyword
            try:
                if bot_command[matched_keyword][4] == False:
                    msg = bot_command[matched_keyword][0]()
                else:
                    msg = bot_command[matched_keyword][0](j)
            except Exception as e:
                print(e)
                msg = ''

            if msg != '':
                # Is keyword suppressed?
                if bot_command[matched_keyword][6] == True:
                    resp['reply'] = msg
                elif bot_command[matched_keyword][4] == False:
                    resp['reply'] = msg + j['suffix']
                else:
                    resp['reply'] = j['at_sender'] + msg
                return resp, 200

        # Postprocessors
        status_code = 204
        for func in self.__postprocessors:
            if func[1] == 0 and j['group_id'] in [int(x) for x in func[2] if x != '']:
                continue
            elif func[1] == 1 and j['group_id'] not in [int(x) for x in func[2] if x != '']:
                continue
            resp_temp, status_code = func[0](j, resp)
            if resp_temp != '':
                resp = resp_temp
            if status_code != 204:
                break

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
            url = f"{self.__getattr(cfg, 'base_url', 'http://127.0.0.1:5700')}/send_group_msg_async"
            for group_id in broadcast_group:
                payload = {
                    'group_id': int(group_id),
                    'message': msg
                }
                requests.post(url, json=payload)

    def tell(self):
        """
        The dragon tells you about what he can do.

        Translate: Return a dictionary of current bot commands.
        """
        # Example:
        # {
        #     "Plugin module name": {
        #         "module.function": ["docstring", "keyword", block/allowlist, ["group_id1", "group_id2"], 
        #         cooldown, is message body required, is keyword regex, is suffix suppressed, is enabled, priority]
        #     }
        # }
        alert_functions = {}
        bot_commands = {}
        preprocessors = {}
        postprocessors = {}

        for command in self.__botcommand.keys():
            module_name = self.__botcommand[command][0].__module__
            if module_name not in bot_commands:
                bot_commands[module_name] = {}
            command_conf = [self.__botcommand[command][0].__doc__, command]
            command_conf.extend(self.__botcommand[command][1:])
            bot_commands[module_name][f'{module_name}.{self.__botcommand[command][0].__name__}'] = command_conf

        for command in self.__alerts.keys():
            module_name = command.__module__
            if module_name not in alert_functions:
                alert_functions[module_name] = {}
            command_conf = [command.__doc__]
            command_conf.extend(self.__alerts[command])
            alert_functions[module_name][f'{module_name}.{command.__name__}'] = command_conf

        for command in self.__preprocessors:
            module_name = command[0].__module__
            if module_name not in preprocessors:
                preprocessors[module_name] = {}
            command_conf = [command[0].__doc__]
            command_conf.extend(command[1:])
            preprocessors[module_name][f'{module_name}.{command[0].__name__}'] = command_conf

        for command in self.__postprocessors:
            module_name = command[0].__module__
            if module_name not in postprocessors:
                postprocessors[module_name] = {}
            command_conf = [command[0].__doc__]
            command_conf.extend(command[1:])
            postprocessors[module_name][f'{module_name}.{command[0].__name__}'] = command_conf

        conf = {
            'alert_functions': alert_functions,
            'bot_commands': bot_commands,
            'preprocessors': preprocessors,
            'postprocessors': postprocessors
        }

        return conf


    def study(self):
        """
        The dragon will study the configurations for each command.

        Translate: Load configurations for each bot_command from `Paarthurnax/settings/settings.json` .
        """
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings', 'settings.json'), 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            settings = {
                'alert_functions': {},
                'bot_commands': {},
                'preprocessors': {},
                'postprocessors': {}
            }

        new_alerts = {}
        try:
            for command in self.__alerts.keys():
                func_name = f'{command.__module__}.{command.__name__}'
                if command.__module__ in settings['alert_functions']:
                    if func_name in settings['alert_functions'][command.__module__]:
                        new_alerts[command] = settings['alert_functions'][command.__module__][func_name]
                    else:
                        new_alerts[command] = [self.__alerts[command], True]
            self.__alerts = new_alerts
        except Exception as e:
            print(e)
            self.__alerts = {}

        new_command = {}
        try:
            for command in self.__botcommand.keys():
                func_name = f'{self.__botcommand[command][0].__module__}.{self.__botcommand[command][0].__name__}'
                if self.__botcommand[command][0].__module__ in settings['bot_commands']:
                    if func_name in settings['bot_commands'][self.__botcommand[command][0].__module__]:
                        func = self.__botcommand[command][0]
                        new_command[settings['bot_commands'][self.__botcommand[command][0].__module__][func_name][0]] = [func] + settings['bot_commands'][self.__botcommand[command][0].__module__][func_name][1:]
                    else:
                        new_command[command] = self.__botcommand[command] + [True, 0]
            self.__botcommand = {k: v for k, v in sorted(new_command.items(), key=lambda item: item[1][-1], reverse=True)}
        except Exception as e:
            print(e)
            self.__botcommand = {}

        new_preprocessors = []
        try:
            for command in self.__preprocessors:
                func_name = f'{command[0].__module__}.{command[0].__name__}'
                if command[0].__module__ in settings['preprocessors']:
                    if func_name in settings['preprocessors'][command[0].__module__]:
                        new_preprocessors.append([command[0]] + settings['preprocessors'][command[0].__module__][func_name])
                    else:
                        new_preprocessors.append(command + [True, 0])
            self.__preprocessors = sorted(new_preprocessors, key=lambda item: item[-1], reverse=True)
        except Exception as e:
            print(e)
            self.__preprocessors = {}

        new_postprocessors = []
        try:
            for command in self.__postprocessors:
                func_name = f'{command[0].__module__}.{command[0].__name__}'
                if command[0].__module__ in settings['postprocessors']:
                    if func_name in settings['postprocessors'][command[0].__module__]:
                        new_postprocessors.append([command[0]] + settings['postprocessors'][command[0].__module__][func_name])
                    else:
                        new_postprocessors.append(command + [True, 0])
            self.__postprocessors = sorted(new_postprocessors, key=lambda item: item[-1], reverse=True)
        except Exception as e:
            print(e)
            self.__postprocessors = {}

    def take(self, config_json):
        """
        The dragon takes the configuration sheet from your hands and studies it.

        Translate: Save config to `Paarthurnax/settings/settings.json` and refresh the current configurations.
        """
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings', 'settings.json'), 'w+', encoding='utf-8') as f:
                f.write(json.dumps(config_json, ensure_ascii=False))
        except Exception as e:
            return 'Something went wrong.', 500
        try:
            self.study()
            for job in self.__schduler.get_jobs():
                job.remove()
            for func in self.__alerts.keys():
                if self.__alerts[func][1]:
                    self.__add_job(func, self.__alerts[func][0])
        except Exception as e:
            settings = {
                'alert_functions': {},
                'bot_commands': {},
                'preprocessors': {},
                'postprocessors': {}
            }
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings', 'settings.json'), 'w+', encoding='utf-8') as f:
                f.write(json.dumps(settings, ensure_ascii=False))
            return 'That page is corrupted and I have burned it to ashes.', 500
        return 'I heed you loud and clear, traveller.', 200

    def query(self, id='', group_id='', sender_id='', message='', timestamp_eq='', timestamp_lt='', timestamp_gt='', order_by='timestamp', desc=True, limit=10):
        """
        The dragon recites things he heard in the past. He has eidetic memory.

        Translate: Query message log using SQL parameters.
        """
        query_string = f'''SELECT id, group_id, sender_id, message, timestamp FROM messages WHERE 1=1 
            {" AND id = ? " if id != "" else ""}
            {" AND group_id = ? " if group_id != "" else ""}
            {" AND sender_id = ? " if sender_id != "" else ""}
            {" AND message = ? " if message != "" else ""}
            {" AND timestamp = ? " if timestamp_eq != "" else ""}
            {" AND timestamp < ? " if timestamp_lt != "" else ""}
            {" AND timestamp > ? " if timestamp_gt != "" else ""}
            {" ORDER BY " + order_by if order_by in ["id", "group_id", "sender_id", "message", "timestamp"] else ""}{" DESC " if desc else " ASC "}{"LIMIT " + str(min(limit,100)) if limit > 0 else ""}'''

        query_params = () + ((id,) if id != "" else ()) + ((group_id,) if group_id != "" else ()) + ((sender_id,) if sender_id != "" else ()) + \
            ((message,) if message != "" else ()) + ((timestamp_eq,) if timestamp_eq != "" else ()) + ((timestamp_lt,) if timestamp_lt != "" else ()) + \
            ((timestamp_gt,) if timestamp_gt != "" else ())

        try:
            db = sqlite3.connect('qqbot.sqlite')
            cursor = db.cursor()
            cursor.execute(query_string, query_params)
            rows = cursor.fetchall()
        except Exception as e:
            print(e)
            rows = []
        finally:
            db.close()
        
        return rows

    def api(self, endpoint, payload={}):
        """
        The dragon tries to do some trivial stuff you tell him to.

        Translate: Access OneBot public API endpoints.
        """
        available_endpoints = [
            'send_private_msg',
            'send_group_msg',
            'send_msg',
            'delete_msg',
            'get_msg',
            'get_forward_msg',
            'send_like',
            'set_group_kick',
            'set_group_ban',
            'set_group_anonymous_ban',
            'set_group_whole_ban',
            'set_group_admin',
            'set_group_anonymous',
            'set_group_card',
            'set_group_name',
            'set_group_leave',
            'set_group_special_title',
            'set_friend_add_request',
            'set_group_add_request',
            'get_login_info',
            'get_stranger_info',
            'get_friend_list',
            'get_group_info',
            'get_group_list',
            'get_group_member_info',
            'get_group_member_list',
            'get_group_honor_info',
            'get_record',
            'get_image',
            'can_send_image',
            'can_send_record'
        ]

        if endpoint in available_endpoints:
            if endpoint in ['send_private_msg', 'send_group_msg', 'send_msg']:
                endpoint += '_rate_limited'
            r = requests.post(url=f"{getattr(self.__cfg, 'base_url', 'http://127.0.0.1:5700')}/{endpoint}", json=payload)
            return r.text, r.status_code