import configparser
from pathlib import Path

CONFIG_PATH = Path.home() / ".automl.ini"

CURRENT_USER_NAME = ""
CURRENT_USER_EMAIL = ""

def load_all_users() -> dict:
    """Return a dictionary mapping user names to emails."""
    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH)
    users = {}
    if parser.has_section('users'):
        users = dict(parser.items('users'))
    elif parser.has_section('user'):  # backward compatibility
        name = parser.get('user', 'name', fallback='')
        email = parser.get('user', 'email', fallback='')
        if name and email:
            users[name] = email
    return users

def get_last_user() -> str:
    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH)
    return parser.get('current', 'name', fallback='')

def load_user_config():
    users = load_all_users()
    last = get_last_user()
    if last and last in users:
        return last, users[last]
    if users:
        name = next(iter(users))
        return name, users[name]
    return "", ""

def save_user_config(name: str, email: str) -> None:
    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH)
    if 'users' not in parser:
        parser['users'] = {}
    parser['users'][name] = email
    if 'current' not in parser:
        parser['current'] = {}
    parser['current']['name'] = name
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        parser.write(f)

def set_last_user(name: str) -> None:
    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH)
    if 'current' not in parser:
        parser['current'] = {}
    parser['current']['name'] = name
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        parser.write(f)

def set_current_user(name: str, email: str) -> None:
    global CURRENT_USER_NAME, CURRENT_USER_EMAIL
    CURRENT_USER_NAME = name
    CURRENT_USER_EMAIL = email
