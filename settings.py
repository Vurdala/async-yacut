import os
import string


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
    MAX_URL_LENGTH = 256
    MAX_LENGTH = 255
    MAX_SHORT_ID_LENGTH = 16
    ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
    SHORT_ID_LENGTH = 6
    MAX_GENERATE_ATTEMPTS = 10
    SHORT_ID_CHARS = string.ascii_letters + string.digits
    RESERVED_SHORTS = {'admin', 'files', 'api', 'static', 'favicon.ico'}
    RESERVED_ENDPOINTS = {'files'}
    YANDEX_DISK_API_BASE = 'https://cloud-api.yandex.net/v1'
    YANDEX_DISK_UPLOAD_URL = YANDEX_DISK_API_BASE + '/disk/resources/upload'
    YANDEX = '/disk/resources/download'
    YANDEX_DISK_DOWNLOAD_URL = YANDEX_DISK_API_BASE + YANDEX
    YANDEX_DISK_PATH_PREFIX = '/uploads/'
    BASE_URL = 'http://localhost'
