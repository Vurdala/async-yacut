import re

from http import HTTPStatus
from flask import request, jsonify

from . import app, db
from .models import URLMap
from .error_handlers import InvalidAPIUsage
from .utils import get_unique_short_id


message = 'Предложенный вариант короткой ссылки уже существует.'


@app.route("/api/id/", methods=["POST"])
def create_short_link():
    if not request.data:
        return jsonify(
            {'message': 'Отсутствует тело запроса'}
        ), HTTPStatus.BAD_REQUEST

    if not request.is_json:
        return jsonify(
            {'message': 'Отсутствует тело запроса'}
        ), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    if data is None:
        return jsonify(
            {'message': 'Тело запроса должно быть в формате JSON'}
        ), HTTPStatus.BAD_REQUEST

    original = data.get("url")
    if not original:
        return jsonify(
            {'message': '"url" является обязательным полем!'}
        ), HTTPStatus.BAD_REQUEST

    custom_id = data.get("custom_id", "").strip()

    if not custom_id:
        short = get_unique_short_id()
    else:
        if len(custom_id) > 16:
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400

        if not re.fullmatch(r"^[a-zA-Z0-9]+$", custom_id):
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400

        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify(
                {'message': f'{message}'}
            ), 400
        short = custom_id

    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()

    return jsonify(
        {"url": original, "short_link": f"{request.host_url}{short}"}
    ), HTTPStatus.CREATED


@app.route("/api/id/<path:short_id>/", methods=["GET"])
def get_opinion(short_id):
    link = URLMap.query.filter_by(short=short_id).first()
    if link is None:
        raise InvalidAPIUsage("Указанный id не найден", HTTPStatus.NOT_FOUND)
    return jsonify({"url": link.original}), HTTPStatus.OK
