from src.utils import get_b64encoded_qr_image
from .forms import LoginForm, RegisterForm, TwoFactorForm
from src.accounts.models import User
from src import db, bcrypt
from flask_login import current_user, login_required, login_user, logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for
from src import login_manager

accounts_bp = Blueprint("accounts", __name__)

HOME_URL = "core.home"
LOGIN_URL = "accounts.login"
SETUP_2FA_URL = "accounts.setup_two_factor_auth"
VERIFY_2FA_URL = "accounts.verify_two_factor_auth"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


#@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if current_user.is_two_factor_authentication_enabled:
            flash("Аккаунт уже зарегистрирован.", "info")
            return redirect(url_for(HOME_URL))
        else:
            flash(
                "Вы не включили двухфакторную аутентификацию. Пожалуйста, сначала включите ее для входа в систему.", "info")
            return redirect(url_for(SETUP_2FA_URL))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash("Вы зарегистрированы. Для входа в систему вам необходимо сначала включить двухфакторную аутентификацию.", "success")

            return redirect(url_for(SETUP_2FA_URL))
        except Exception:
            db.session.rollback()
            flash("Не удалось зарегистрироваться. Пожалуйста, попробуйте снова.", "danger")

    return render_template("accounts/register.html", form=form)


@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_two_factor_authentication_enabled and current_user.is_two_factor_authenticated:
            flash("Вы уже вошли в аккаунт.", "info")
            return redirect(url_for(HOME_URL))
        elif not current_user.is_two_factor_authentication_enabled:
            flash(
                "Вы не включили двухфакторную аутентификацию. Пожалуйста, сначала включите ее для входа в систему.", "info")
            return redirect(url_for(SETUP_2FA_URL))
        else: 
            flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
            return redirect(url_for(VERIFY_2FA_URL))
        
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            if not current_user.is_two_factor_authentication_enabled:
                flash(
                    "Вы не включили двухфакторную аутентификацию. Пожалуйста, сначала включите ее для входа в систему.", "info")
                return redirect(url_for(SETUP_2FA_URL))
            return redirect(url_for(VERIFY_2FA_URL))
        elif not user:
            flash("Вы не зарегистрированы. Пожалуйста, обратитесь к администратору", "danger")
        else:
            flash("Неверное имя пользователя или пароль.", "danger")
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/logout")
@login_required
def logout():
    try:
        current_user.is_two_factor_authenticated = False
        db.session.commit()
        logout_user()
        flash("Вы вышли из аккаунта.", "success")
    except Exception:
            db.session.rollback()
            flash("Не удалось выйти из аккаунта. Пожалуйста, попробуйте снова.", "danger")
    
    return redirect(url_for(LOGIN_URL))



@accounts_bp.route("/setup-2fa")
@login_required
def setup_two_factor_auth():
    secret = current_user.secret_token
    uri = current_user.get_authentication_setup_uri()
    base64_qr_image = get_b64encoded_qr_image(uri)
    return render_template("accounts/setup-2fa.html", secret=secret, qr_image=base64_qr_image)


@accounts_bp.route("/verify-2fa", methods=["GET", "POST"])
@login_required
def verify_two_factor_auth():
    form = TwoFactorForm(request.form)
    if form.validate_on_submit():
        if current_user.is_otp_valid(form.otp.data):
            try:
                if current_user.is_two_factor_authentication_enabled:
                    current_user.is_two_factor_authenticated = True
                    db.session.commit()
                    flash("Двухфакторная аутентификация прошла успешно. Вы вошли в аккаунт!", "success")
                    return redirect(url_for(HOME_URL))
                else:
                    current_user.is_two_factor_authenticated = True
                    current_user.is_two_factor_authentication_enabled = True
                    db.session.commit()
                    flash("Двухфакторная аутентификация прошла успешно. Вы вошли в систему!", "success")
                    return redirect(url_for(HOME_URL))
            except Exception:
                    db.session.rollback()
                    flash("Не удалось настроить двухфакторную аутентификацию. Пожалуйста, попробуйте снова.", "danger")
                    return redirect(url_for(VERIFY_2FA_URL))
        else:
            flash("Недействительный OTP. Пожалуйста, попробуйте снова.", "danger")
            return redirect(url_for(VERIFY_2FA_URL))
    else:
        if not current_user.is_two_factor_authentication_enabled:
            flash(
                "Вы не включили двухфакторную аутентификацию. Пожалуйста, сначала включите ее.", "info")
        return render_template("accounts/verify-2fa.html", form=form)
