from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    IntegerField,
    TextAreaField,
    SelectMultipleField,
    FileField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange
)


class BookForm(FlaskForm):

    title = StringField(
        "Название",
        validators=[
            DataRequired(),
            Length(max=255)
        ]
    )

    description = TextAreaField(
        "Описание",
        validators=[
            DataRequired()
        ]
    )

    year = IntegerField(
        "Год",
        validators=[
            DataRequired()
        ]
    )

    publisher = StringField(
        "Издательство",
        validators=[
            DataRequired()
        ]
    )

    author = StringField(
        "Автор",
        validators=[
            DataRequired()
        ]
    )

    pages = IntegerField(
        "Страниц",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    genres = SelectMultipleField(
        "Жанры",
        coerce=int
    )

    cover = FileField(
        "Обложка"
    )

    submit = SubmitField(
        "Сохранить"
    )