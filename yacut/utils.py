import string
import random
from .models import URLMap
from flask import abort


def get_unique_short_id(length=6):
    chars = string.ascii_letters + string.digits
    for _ in range(10):
        short_id = "".join(random.choices(chars, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    abort(500)
