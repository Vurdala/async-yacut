from datetime import datetime
import random

from flask import url_for

from yacut import db
from .error_handlers import (
    ERROR_INVALID_SHORT, ERROR_INVALID_URL, ERROR_SHORT_EXISTS
)
from settings import (
    MAX_URL_LENGTH,
    MAX_SHORT_LENGTH,
    MAX_GENERATE_ATTEMPTS,
    SHORT_CHARS,
    SHORT_LENGTH,
    SHORT_LINK_VIEW_NAME,
    SHORT_PATTERN,
    RESERVED_SHORTS,
)


UNIQUE_SHORT_GENERATION_ERROR = (
    'Не удалось сгенерировать уникальный короткий идентификатор'
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_or_404(short):
        return URLMap.query.filter_by(short=short).first_or_404()

    @staticmethod
    def create(
        original, short=None,
        validate: bool = True,
        commit: bool = True
    ):
        if not short:
            short = URLMap._generate_unique_short()

        if validate and len(short) > MAX_SHORT_LENGTH:
            raise ValueError(ERROR_INVALID_SHORT)

        if (
            validate
            and not SHORT_PATTERN.fullmatch(short)
        ):
            raise ValueError(ERROR_INVALID_SHORT)

        if validate and len(original) > MAX_URL_LENGTH:
            raise ValueError(ERROR_INVALID_URL)

        if (
            (validate and short in RESERVED_SHORTS)
            or URLMap.query.filter_by(short=short).first()
        ):
            raise ValueError(ERROR_SHORT_EXISTS)

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        if commit:
            db.session.commit()
        return url_map

    @staticmethod
    def _generate_unique_short():
        for _ in range(MAX_GENERATE_ATTEMPTS):
            short = "".join(
                random.choices(SHORT_CHARS, k=SHORT_LENGTH)
            )
            if short not in RESERVED_SHORTS and not URLMap.query.filter_by(
                short=short
            ).first():
                return short
        raise RuntimeError(UNIQUE_SHORT_GENERATION_ERROR)

    def get_short_link(self):
        return url_for(
            SHORT_LINK_VIEW_NAME,
            short=self.short,
            _external=True,
        )

    def __repr__(self):
        return f"<URLMap {self.short}>"
