import csv

from io import StringIO

from flask import (
    Blueprint,
    render_template,
    request,
    Response,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy import func

from datetime import datetime

from models import (
    db,
    Book,
    BookView,
    VisitLog
)

statistics_bp = Blueprint(
    "statistics",
    __name__,
    url_prefix="/statistics"
)


def admin_required():

    if not current_user.is_authenticated:
        return False

    if not current_user.role:
        return False

    return (
        current_user.role.name.lower()
        == "admin"
    )


@statistics_bp.route("/")
@login_required
def index():

    if not admin_required():

        return redirect(
            url_for("books.index")
        )

    start_date = request.args.get(
        "start_date"
    )

    end_date = request.args.get(
        "end_date"
    )

    visits_query = (
        VisitLog.query
        .order_by(
            VisitLog.viewed_at.desc()
        )
    )

    books_query = (
        db.session.query(
            Book,
            func.count(
                BookView.id
            ).label("views")
        )
        .outerjoin(
            BookView,
            Book.id == BookView.book_id
        )
    )

    if start_date and end_date:

        try:

            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            )

            visits_query = (
                visits_query.filter(
                    VisitLog.viewed_at >= start,
                    VisitLog.viewed_at <= end
                )
            )

            books_query = (
                books_query.filter(
                    BookView.viewed_at >= start,
                    BookView.viewed_at <= end
                )
            )

        except ValueError:
            pass

    visits = (
        visits_query
        .limit(500)
        .all()
    )

    books_stats = (
        books_query
        .group_by(Book.id)
        .order_by(
            func.count(
                BookView.id
            ).desc()
        )
        .all()
    )

    return render_template(
        "statistics/index.html",
        visits=visits,
        books_stats=books_stats,
        start_date=start_date,
        end_date=end_date
    )


@statistics_bp.route(
    "/export-visits"
)
@login_required
def export_visits():

    if not admin_required():

        return redirect(
            url_for(
                "books.index"
            )
        )

    visits = (
        VisitLog.query
        .order_by(
            VisitLog.viewed_at.desc()
        )
        .all()
    )

    output = StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow([
        "Пользователь",
        "Книга",
        "Дата"
    ])

    for visit in visits:

        writer.writerow([

            visit.user.full_name
            if visit.user
            else "Гость",

            visit.book.title,

            visit.viewed_at

        ])

    csv_data = output.getvalue()

    return Response(
        "\ufeff" + csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                "attachment; filename=visits.csv"
        }
    )


@statistics_bp.route(
    "/export-books"
)
@login_required
def export_books():

    if not admin_required():

        return redirect(
            url_for(
                "books.index"
            )
        )

    books_stats = (
        db.session.query(
            Book,
            func.count(
                BookView.id
            ).label("views")
        )
        .outerjoin(
            BookView,
            Book.id == BookView.book_id
        )
        .group_by(
            Book.id
        )
        .order_by(
            func.count(
                BookView.id
            ).desc()
        )
        .all()
    )

    output = StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow([
        "Книга",
        "Просмотры"
    ])

    for book, views in books_stats:

        writer.writerow([
            book.title,
            views
        ])

    csv_data = output.getvalue()

    return Response(
        "\ufeff" + csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                "attachment; filename=books.csv"
        }
    )