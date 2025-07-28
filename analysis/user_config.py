import configparser
from pathlib import Path

CONFIG_PATH = Path.home() / ".automl.ini"

CURRENT_USER_NAME = ""
CURRENT_USER_EMAIL = ""

def load_user_config():
    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH)
    name = parser.get('user', 'name', fallback='')
    email = parser.get('user', 'email', fallback='')
    return name, email

def save_user_config(name: str, email: str) -> None:
    parser = configparser.ConfigParser()
    parser['user'] = {'name': name, 'email': email}
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        parser.write(f)

def set_current_user(name: str, email: str) -> None:
    global CURRENT_USER_NAME, CURRENT_USER_EMAIL
    CURRENT_USER_NAME = name
    CURRENT_USER_EMAIL = email
