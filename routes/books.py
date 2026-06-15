import os
import hashlib

from forms.review_form import ReviewForm
from flask_login import current_user
from sqlalchemy import func
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app
)

from flask_login import (
    current_user,
    login_required
)

from sqlalchemy import func

import bleach
import markdown

from models import (
    db,
    Book,
    Genre,
    Cover,
    Review,
    BookView,
    VisitLog
)

from forms.book_form import BookForm

from utils.permissions import roles_required


books_bp = Blueprint(
    "books",
    __name__
)


@books_bp.route("/")
def index():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    books = (
        Book.query
        .order_by(Book.year.desc())
        .paginate(
            page=page,
            per_page=10
        )
    )

    popular_books = (
        db.session.query(
            Book,
            func.count(BookView.id)
        )
        .outerjoin(BookView)
        .group_by(Book.id)
        .order_by(
            func.count(
                BookView.id
            ).desc()
        )
        .limit(5)
        .all()
    )

    recent_books = []

    if current_user.is_authenticated:

        recent_books = (
            db.session.query(Book)
            .join(BookView)
            .filter(
                BookView.user_id ==
                current_user.id
            )
            .order_by(
                BookView.viewed_at.desc()
            )
            .limit(5)
            .all()
        )

    return render_template(
        "index.html",
        books=books,
        popular_books=popular_books,
        recent_books=recent_books
    )


@books_bp.route("/book/<int:book_id>")
def detail(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    html_description = markdown.markdown(
        book.description
    )

    if current_user.is_authenticated:

        today = datetime.utcnow().date()

        views_today = (
            BookView.query
            .filter(
                BookView.user_id == current_user.id,
                BookView.book_id == book.id,
                func.date(BookView.viewed_at) == today
            )
            .count()
        )

        if views_today < 10:

            view = BookView(
                user_id=current_user.id,
                book_id=book.id
            )

            db.session.add(view)

            log = VisitLog(
                user_id=current_user.id,
                book_id=book.id
            )

            db.session.add(log)

            db.session.commit()

    reviews = (
        Review.query
        .filter_by(
            book_id=book.id
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )

    user_review = None

    if current_user.is_authenticated:

        user_review = (
            Review.query
            .filter_by(
                book_id=book.id,
                user_id=current_user.id
            )
            .first()
        )

    return render_template(
        "book_detail.html",
        book=book,
        html_description=html_description,
        reviews=reviews,
        user_review=user_review
    )


@books_bp.route(
    "/book/create",
    methods=["GET", "POST"]
)
@login_required
@roles_required("admin")
def create():

    form = BookForm()

    form.genres.choices = [
        (
            g.id,
            g.name
        )
        for g in Genre.query.order_by(
            Genre.name
        )
    ]

    if form.validate_on_submit():

        try:

            description = bleach.clean(
                form.description.data
            )

            book = Book(
                title=form.title.data,
                description=description,
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data
            )

            db.session.add(book)

            db.session.flush()

            selected_genres = (
                Genre.query.filter(
                    Genre.id.in_(
                        form.genres.data
                    )
                ).all()
            )

            book.genres = selected_genres

            file = form.cover.data

            if file:

                content = file.read()

                md5_hash = hashlib.md5(
                    content
                ).hexdigest()

                file.seek(0)

                cover = Cover(
                file_name="",
                mime_type=file.mimetype,
                md5_hash=md5_hash,
                book_id=book.id
            )

                db.session.add(cover)

                db.session.flush()

                ext = os.path.splitext(
                    file.file_name
                )[1]

                file_name = (
                    f"{cover.id}{ext}"
                )

                upload_dir = (
                    current_app.config[
                        "UPLOAD_FOLDER"
                    ]
                )

                os.makedirs(
                    upload_dir,
                    exist_ok=True
                )

                file_path = os.path.join(
                    upload_dir,
                    file_name
                )

                print("UPLOAD DIR:", upload_dir)
                print("FILE PATH:", file_path)

                file.save(file_path)

                print("EXISTS:", os.path.exists(file_path))

                cover.file_name = file_name

            db.session.commit()

            flash(
                "Книга успешно добавлена",
                "success"
            )

            return redirect(
                url_for(
                    "books.detail",
                    book_id=book.id
                )
            )

        except Exception as e:

            db.session.rollback()

            flash(
                "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
                "danger"
            )

    return render_template(
        "book_create.html",
        form=form
    )


@books_bp.route(
    "/book/<int:book_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@roles_required(
    "admin",
    "moderator"
)
def edit(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    form = BookForm(
        obj=book
    )

    form.genres.choices = [
        (
            g.id,
            g.name
        )
        for g in Genre.query.order_by(
            Genre.name
        )
    ]

    if request.method == "GET":

        form.genres.data = [
            g.id
            for g in book.genres
        ]

    if form.validate_on_submit():

        try:

            book.title = form.title.data

            book.description = bleach.clean(
                form.description.data
            )

            book.year = form.year.data

            book.publisher = (
                form.publisher.data
            )

            book.author = (
                form.author.data
            )

            book.pages = (
                form.pages.data
            )

            genres = (
                Genre.query.filter(
                    Genre.id.in_(
                        form.genres.data
                    )
                ).all()
            )

            book.genres = genres

            file = request.files.get("cover")

            if file and file.filename:

                content = file.read()

                md5_hash = hashlib.md5(
                    content
                ).hexdigest()

                file.seek(0)

                ext = os.path.splitext(
                    file.filename
                )[1]

                if book.cover:

                    old_path = os.path.join(
                        current_app.config[
                            "UPLOAD_FOLDER"
                        ],
                        book.cover.file_name
                    )

                    if os.path.exists(
                        old_path
                    ):
                        os.remove(
                            old_path
                        )

                    file_name = (
                        f"{book.cover.id}{ext}"
                    )

                    book.cover.mime_type = (
                        file.mimetype
                    )

                    book.cover.md5_hash = (
                        md5_hash
                    )

                else:

                    cover = Cover(
                        file_name="",
                        mime_type=file.mimetype,
                        md5_hash=md5_hash,
                        book_id=book.id
                    )

                    db.session.add(
                        cover
                    )

                    db.session.flush()

                    file_name = (
                        f"{cover.id}{ext}"
                    )

                    book.cover = cover

                file_path = os.path.join(
                    current_app.config[
                        "UPLOAD_FOLDER"
                    ],
                    file_name
                )

                file.save(
                    file_path
                )

                book.cover.file_name = (
                    file_name
                )

            db.session.commit()

            flash(
                "Книга успешно обновлена",
                "success"
            )

            return redirect(
                url_for(
                    "books.detail",
                    book_id=book.id
                )
            )

        except Exception as e:

            db.session.rollback()

            flash(
                f"Ошибка сохранения: {e}",
                "danger"
            )

    return render_template(
        "book_edit.html",
        form=form,
        book=book
    )


@books_bp.route(
    "/book/<int:book_id>/delete",
    methods=["POST"]
)
@login_required
@roles_required(
    "admin"
)
def delete(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    try:

        if book.cover:

            path = os.path.join(
                current_app.config[
                    "UPLOAD_FOLDER"
                ],
                book.cover.file_name
            )

            if os.path.exists(path):
                os.remove(path)

        db.session.delete(book)

        db.session.commit()

        flash(
            "Книга успешно удалена",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Ошибка удаления книги",
            "danger"
        )

    return redirect(
        url_for("books.index")
    )

@books_bp.route(
    "/book/<int:book_id>/review",
    methods=["GET", "POST"]
)
@login_required
def create_review(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    existing_review = Review.query.filter_by(
        book_id=book.id,
        user_id=current_user.id
    ).first()

    if existing_review:

        flash(
            "Вы уже оставляли рецензию на эту книгу",
            "warning"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    form = ReviewForm()

    if form.validate_on_submit():

        try:

            review = Review(
                book_id=book.id,
                user_id=current_user.id,
                rating=form.rating.data,
                text=bleach.clean(
                    form.text.data
                )
            )

            db.session.add(review)

            db.session.commit()

            flash(
                "Рецензия успешно добавлена",
                "success"
            )

            return redirect(
                url_for(
                    "books.detail",
                    book_id=book.id
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Ошибка сохранения рецензии",
                "danger"
            )

    return render_template(
        "review_create.html",
        form=form,
        book=book
    )