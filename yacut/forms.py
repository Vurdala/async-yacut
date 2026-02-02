from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional


class URLForm(FlaskForm):
    original_link = (
        URLField(
            "Введите ссылку",
            validators=[DataRequired(message="Обязательное поле"), Length(1, 128)],
        ),
    )
    custom_id = (
        (
            StringField(
                "Введите короткий идентификатор", validators=[Optional(), Length(1, 16)]
            )
        ),
    )
    submit = SubmitField("Сократить ссылку")


class FileForm(FlaskForm):
    files = FileField(
        "Файл для загрузки",
        validators=[
            DataRequired(), FileAllowed(["jpg", "png", "jpeg", "gif"])
        ],
    )
