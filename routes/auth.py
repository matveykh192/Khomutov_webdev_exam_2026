from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for
)

from flask_login import (
    login_user,
    logout_user,
    login_required
)

from werkzeug.security import check_password_hash

from models import User

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login = request.form.get("login")
        password = request.form.get("password")

        user = User.query.filter_by(
            login=login
        ).first()

        if (
            user
            and check_password_hash(
                user.password_hash,
                password
            )
        ):
            login_user(user)

            flash(
                "Вход выполнен успешно",
                "success"
            )

            return redirect(
                url_for("books.index")
            )

        flash(
            "Невозможно аутентифицироваться с указанными логином и паролем",
            "danger"
        )

    return render_template(
        "login.html"
    )


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "Вы успешно вышли из системы",
        "success"
    )

    return redirect(
        url_for("books.index")
    )