from http import HTTPStatus

from flask import request, jsonify

from . import app
from .error_handlers import (
    InvalidAPIUsage, ERROR_NO_BODY,
    ERROR_NO_JSON, ERROR_NO_URL
)
from .models import URLMap


@app.route("/api/id/", methods=["POST"])
def create_short_link():
    if not request.is_json:
        raise InvalidAPIUsage(ERROR_NO_JSON)

    data = request.get_json(silent=True)

    if data is None:
        raise InvalidAPIUsage(ERROR_NO_BODY)

    if "url" not in data:
        raise InvalidAPIUsage(ERROR_NO_URL)
    try:
        url_map = URLMap.create(
            original=data["url"],
            short=data.get("custom_id")
        )
    except ValueError as e:
        raise InvalidAPIUsage(str(e))

    return (
        jsonify(
            {
                "url": data["url"],
                "short_link": url_map.get_short_link()
            }
        ),
        HTTPStatus.CREATED,
    )


@app.route("/api/id/<path:short>/", methods=["GET"])
def get_opinion(short):
    return jsonify({"url": URLMap.get_or_404(short).original}), HTTPStatus.OK
