from http import HTTPStatus

from flask import jsonify, render_template, request

from . import app, db


ERROR_NO_BODY = 'Отсутствует тело запроса'
ERROR_NO_JSON = 'Тело запроса должно быть в формате JSON'
ERROR_NO_URL = '"url" является обязательным полем!'
ERROR_INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
ERROR_SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
ERROR_NOT_FOUND = 'Указанный id не найден'


class InvalidAPIUsage(Exception):
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    db.session.rollback()
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'message': ERROR_NOT_FOUND}), HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND
