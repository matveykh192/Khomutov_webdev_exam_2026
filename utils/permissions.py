from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for

from flask_login import current_user


def roles_required(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:

                flash(
                    "Для выполнения данного действия необходимо пройти процедуру аутентификации",
                    "warning"
                )

                return redirect(
                    url_for("auth.login")
                )

            allowed = False

            for role in roles:

                if (
                    current_user.role
                    and
                    current_user.role.name.lower()
                    == role.lower()
                ):
                    allowed = True
                    break

            if not allowed:

                flash(
                    "У вас недостаточно прав для выполнения данного действия",
                    "danger"
                )

                return redirect(
                    url_for("books.index")
                )

            return func(
                *args,
                **kwargs
            )

        return wrapper

    return decorator