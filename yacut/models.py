from datetime import datetime
import random

from flask import abort, url_for

from yacut import db
from .error_handlers import ERROR_INVALID_SHORT, ERROR_SHORT_EXISTS
from settings import (
    Config, MAX_LENGTH,
    MAX_SHORT_ID_LENGTH, MAX_GENERATE_ATTEMPTS,
    SHORT_ID_LENGTH
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_LENGTH), nullable=False)
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

        if short in {'admin', 'files', 'api', 'static', 'favicon.ico'}:
            raise ValueError(ERROR_SHORT_EXISTS)

        if len(short) > MAX_SHORT_ID_LENGTH:
            raise ValueError(ERROR_INVALID_SHORT)

        if not Config.SHORT_ID_PATTERN.fullmatch(short):
            raise ValueError(ERROR_INVALID_SHORT)

        if cls.query.filter_by(short=short).first():
            raise ValueError(ERROR_SHORT_EXISTS)

        url_map = cls(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @classmethod
    def _generate_unique_short(cls):
        for _ in range(MAX_GENERATE_ATTEMPTS):
            short = "".join(
                random.choices(Config.SHORT_ID_CHARS, k=SHORT_ID_LENGTH)
            )
            if not cls.query.filter_by(short=short).first():
                return short
        abort(500)

    @staticmethod
    def _is_valid_chars(s):
        return all(c in Config.SHORT_ID_CHARS for c in s)

    def get_short_link(self):
        return url_for(
            Config.SHORT_LINK_VIEW_NAME,
            short=self.short,
            _external=True,
        )

    def to_dict(self):
        return {
            "url": self.original,
            "short_link": f"/{self.short}",
        }

    def __repr__(self):
        return f"<URLMap {self.short}>"
