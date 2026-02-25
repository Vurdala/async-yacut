from datetime import datetime
import re
import random

from flask import abort

from yacut import db
from .error_handlers import (
    InvalidAPIUsage,
    ERROR_INVALID_SHORT,
    ERROR_NOT_FOUND,
    ERROR_SHORT_EXISTS,
)
from settings import Config


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(Config.MAX_LENGTH), nullable=False)
    short = db.Column(db.String(Config.MAX_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_or_404(short):
        url_map = URLMap.query.filter_by(short=short).first()
        if url_map is None:
            abort(404)
        return url_map

    @classmethod
    def create(cls, original, short=None):
        if not short:
            short = cls._generate_unique_short()

        if short in Config.RESERVED_SHORTS:
            raise InvalidAPIUsage(ERROR_SHORT_EXISTS)

        if len(short) > Config.MAX_SHORT_ID_LENGTH:
            raise InvalidAPIUsage(ERROR_INVALID_SHORT)

        if not re.fullmatch(r"^[a-zA-Z0-9]+$", short):
            raise InvalidAPIUsage(ERROR_INVALID_SHORT)

        if cls.query.filter_by(short=short).first():
            raise InvalidAPIUsage(ERROR_SHORT_EXISTS)

        url_map = cls(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @classmethod
    def _generate_unique_short(cls):
        for _ in range(Config.MAX_GENERATE_ATTEMPTS):
            short = "".join(
                random.choices(Config.SHORT_ID_CHARS, k=Config.SHORT_ID_LENGTH)
            )
            if not cls.query.filter_by(short=short).first():
                return short
        abort(500)

    @staticmethod
    def _is_valid_chars(s):
        return all(c in Config.SHORT_ID_CHARS for c in s)

    def to_dict(self):
        return {
            "url": self.original,
            "short_link": f"/{self.short}",
        }

    def __repr__(self):
        return f"<URLMap {self.short}>"
