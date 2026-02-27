import re
import os
import string


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
    ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
    SHORT_ID_CHARS = string.ascii_letters + string.digits
    RESERVED_ENDPOINTS = {'files'}

    YANDEX_DISK_PATH_PREFIX = '/uploads/'
    SHORT_LINK_VIEW_NAME = 'redirect_view'
    SHORT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9]*$')
    YANDEX_DISK_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


YANDEX_DISK_API_BASE = 'https://cloud-api.yandex.net/v1'
YANDEX_DISK_UPLOAD_URL = YANDEX_DISK_API_BASE + '/disk/resources/upload'
YANDEX = '/disk/resources/download'
YANDEX_DISK_DOWNLOAD_URL = YANDEX_DISK_API_BASE + YANDEX
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
SHORT_ID_LENGTH = 6
MAX_GENERATE_ATTEMPTS = 10
SHORT_ID_CHARS = string.ascii_letters + string.digits
MAX_URL_LENGTH = 256
MAX_LENGTH = 255
MAX_SHORT_ID_LENGTH = 16
