import os
import internal
import json

default_settings = {
    'base_url': 'http://127.0.0.1:5700',
    'trivia_enable': False,
    'noh_whitelist': [],
    'suffix': '\n更多命令请输入"帮助"。',
    'approve': True,
    'banned_sender': [],
    'enable_broadcast': False,
    'broadcast_group': [],
    'ban_word': [],
    'ban_duration': 300,
    'reload_token': '',
    'custom_title': {
        'default': '',
        10000: {
            'default': '',
            10000: '',
        }
    },
    'bot_command': {},
}

def convert_legacy_cfg(legacy_cfg):
    save(legacy_cfg)

    with open('ignoreconfig', 'w+') as E:
        E.write('config.py is deprecated, use settings/settings.json instead')

def save(cfg):
    """
    Convert an actual cfg to settings.json
    """
    settings = {}
    bot_command = {}

    for config in default_settings.keys():
        if isinstance(cfg, dict):
            if cfg.get(config, None):
                settings[config] = cfg.get(config, '')
        else:
            if getattr(cfg, config, None):
                settings[config] = getattr(cfg, config, '')

    if isinstance(cfg, dict):
        if cfg.get('bot_command', None):
            for command in cfg.get('bot_command', {}).keys():
                fun = cfg.get('bot_command', {command:['']})[command][0]
                bot_command[f'{fun.__module__}.{fun.__name__}'] = [True, command]
                bot_command[f'{fun.__module__}.{fun.__name__}'].extend(cfg.get('bot_command', {command:['', '']})[command][1:])
    else:
        if getattr(cfg, 'bot_command', None):
            for command in getattr(cfg, 'bot_command', {}).keys():
                fun = getattr(cfg, 'bot_command', {command:['']})[command][0]
                bot_command[f'{fun.__module__}.{fun.__name__}'] = [True, command]
                bot_command[f'{fun.__module__}.{fun.__name__}'].extend(getattr(cfg, 'bot_command', {command:['', '']})[command][1:])

    settings['bot_command'] = bot_command
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings' ,'settings.json') , 'w+', encoding='utf-8') as E:
            json.dump(settings, E, ensure_ascii=False)
    except Exception:
        return False
    return True

def parse_or_load(settings=None):
    """
    Convert a settings.json format to actual cfg format
    """
    bot_command = {}
    cfg = {}

    if not settings:
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'settings' ,'settings.json') , 'r', encoding='utf-8') as E:
                raw_cfg = json.loads(E.read())
        except Exception as e:
            raw_cfg = {}
    else:
        raw_cfg = settings

    for config in default_settings.keys():
        if raw_cfg.get(config, None):
            cfg[config] = raw_cfg.get(config)
        else:
            cfg[config] = default_settings[config]
    
    raw_command = raw_cfg.get('bot_command', {})

    for command in raw_command.keys():
        if command in internal.bot_command_default.keys():
            try:
                if raw_command[command][0]:
                    try:
                        bot_command[internal.bot_command_default[command][1]] = raw_command[command][2:]
                    except Exception:
                        bot_command[internal.bot_command_default[command][1]] = internal.bot_command_default[command][2:]
            except Exception:
                pass

    cfg['bot_command'] = bot_command

    return cfg