from http import HTTPStatus
from flask import request, jsonify, url_for

from . import app
from .models import URLMap
from .error_handlers import (
    InvalidAPIUsage, ERROR_NO_BODY,
    ERROR_NO_JSON, ERROR_NO_URL
)


@app.route("/api/id/", methods=["POST"])
def create_short_link():
    if not request.is_json:
        raise InvalidAPIUsage(
            ERROR_NO_JSON, status_code=HTTPStatus.BAD_REQUEST
        )

    data = request.get_json(silent=True)

    if data is None:
        raise InvalidAPIUsage(
            ERROR_NO_BODY, status_code=HTTPStatus.BAD_REQUEST
        )

    if "url" not in data:
        raise InvalidAPIUsage(ERROR_NO_URL, status_code=HTTPStatus.BAD_REQUEST)

    custom_id = data.get("custom_id")

    url_map = URLMap.create(original=data["url"], short=custom_id)
    return (
        jsonify(
            {
                "url": url_map.original,
                "short_link": url_for(
                    "redirect_view", short=url_map.short, _external=True
                ),
            }
        ),
        HTTPStatus.CREATED,
    )


@app.route("/api/id/<path:short>/", methods=["GET"])
def get_opinion(short):
    url_map = URLMap.get_or_404(short)
    return jsonify({"url": url_map.original}), HTTPStatus.OK
