<<<<<<< HEAD
import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
=======
import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
>>>>>>> 49d2e9456624819a7595eae1ed67115cd43bd364
    DISK_TOKEN = os.getenv("DISK_TOKEN")