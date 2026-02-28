import re
import os
import string


SHORT_CHARS = string.ascii_letters + string.digits
SHORT_PATTERN = re.compile(r'^[{0}]*$'.format(SHORT_CHARS))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
    RESERVED_ENDPOINTS = {'files'}

    YANDEX_DISK_API_BASE = 'https://cloud-api.yandex.net/v1'
    YANDEX_DISK_UPLOAD_URL = (
        f'{YANDEX_DISK_API_BASE}/disk/resources/upload'
    )
    YANDEX_DISK_DOWNLOAD_PATH = '/disk/resources/download'
    YANDEX_DISK_DOWNLOAD_URL = (
        f'{YANDEX_DISK_API_BASE}{YANDEX_DISK_DOWNLOAD_PATH}'
    )
    YANDEX_DISK_PATH_PREFIX = '/uploads/'
    YANDEX_DISK_HEADERS = {
        'Authorization': f'OAuth {DISK_TOKEN}'
    }

    ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
    SHORT_LINK_VIEW_NAME = 'redirect_view'
    SHORT_CHARS = SHORT_CHARS
    SHORT_PATTERN = SHORT_PATTERN


SHORT_LENGTH = 6
MAX_GENERATE_ATTEMPTS = 10
MAX_URL_LENGTH = 2048
MAX_SHORT_LENGTH = 16

RESERVED_SHORT_CODES = {'admin', 'api', 'static', 'favicon.ico'}
RESERVED_SHORTS = {'files'} | RESERVED_SHORT_CODES
