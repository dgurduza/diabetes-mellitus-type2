from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired

from src.accounts.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Пароли не совпадают."),
        ],
    )

    def validate(self, extra_validators):
        initial_validation = super(RegisterForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Пользователь с таким логином уже зарегистрирован.")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Пароли не совпадают.")
            return False
        return True


class AnaliticsForm(FlaskForm):

    variable = SelectField(
        "Переменная",
        validators=[DataRequired()],
        choices=[
            ("gender", "Пол"),
            ("surgery_type", "Тип операции"),
            ("therapy_before_surgery", "Сахароснижающая терапия до операции"),
            ("arterial_hypertension_degree", "Степень артериальной гипертензии"),
            ("dyslipidemia", "Дислипидемия"),
            ("heredity", "Наследственность по ожирению и СД2"),
            ("complications_history", "Осложнения Сахарного диабета 2 типа в анамнезе"),
            ("gestational_diabetes", "Гестационный Сахарный Диабет в анамнезе"),
            ("X1_age_at_surgery", "Возраст на момент проведения операции"),
            ("X2_period_after_surgery", "Длительность периода после операции"),
            ("X3_max_BMI_before_surgery", "Максимальный ИМТ до операции"),
            ("X4_BMI_before_surgery", "ИМТ перед операцией"),
            ("X5_BMI_at_survey", "ИМТ на момент опроса"),
            ("X6_birth_weight", "Масса тела при рождении"),
            ("X7_min_BMI_after_surgery", "Минимальный ИМТ после операции"),
            ("X8_illness_duration", "Длительность СД2"),
            (
                "X9_HbA1c_before_surgery",
                "Уровень гликированного гемоглобина в крови до операции",
            )
        ]
    )

    def validate(self, extra_validators):
        initial_validation = super(AnaliticsForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        return True
