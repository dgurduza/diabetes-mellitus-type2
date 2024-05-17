from flask_wtf import FlaskForm
from datetime import datetime, timedelta
from wtforms import StringField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

from src.calculator.models import Patient

class CalculateForm(FlaskForm):
    survey_date = DateField(
        "Дата опроса", validators=[DataRequired()]
    )
    fullname = StringField(
        "Фамилия Имя Отчество", validators=[DataRequired(), Length(min=4, max=50)]
    )
    birthdate = DateField(
        "Дата рождения", validators=[DataRequired()]
    )
    gender = SelectField(
        "Пол", validators=[DataRequired()], choices=[("Ж", "Ж"), ("М", "М")]
    )
    height = DecimalField(
        "Рост",
        validators=[DataRequired(),
            NumberRange(min=1.0, max=2.7, message="Введите корректное значение")],
        places=4
    )
    X6_birth_weight = DecimalField(
        "Масса тела при рождении",
        validators=[DataRequired(),
            NumberRange(min=0.5, max=6, message="Введите корректное значение")],
        places=4
    )
    weight = DecimalField(
        "Масса тела на момент опроса",
        validators=[DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение")],
        places=4
    )
    diagnosis_date = DateField(
        "Дата диагностирования СД2", validators=[DataRequired()]
    )
    surgery_type = SelectField(
        "Тип операции",
        validators=[DataRequired()],
        choices=[
            ("Продольная резекция желудка", "Продольная резекция желудка"),
            ("Гастрошунтирование", "Гастрошунтирование"),
            ("Билиопанкреатическое шунтирование", "Билиопанкреатическое шунтирование")]
    )
    surgery_date = DateField(
        "Дата операции", validators=[DataRequired()]
    )
    max_weight_before_surgery = DecimalField(
        "Максимальная масса тела до операции",
        validators=[DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение")],
        places=4
    )
    weight_before_surgery = DecimalField(
        "Масса тела перед операцией",
        validators=[DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение")],
        places=4
    )
    min_weight_after_surgery = DecimalField(
        "Минимальная масса тела после операции",
        validators=[DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение")],
        places=4
    )
    therapy_before_surgery = SelectField(
        "Тип сахароснижающей терапии до операции",
        validators=[DataRequired()],
        choices=[
            ("Монотерапия без инсулина", "Монотерапия без инсулина"),
            (
                "Комбинированная терапия без инсулина",
                "Комбинированная терапия без инсулина"
            ),
            ("Терапия с инсулином", "Терапия с инсулином")]
    )
    arterial_hypertension_degree = SelectField(
        "Степень Артериальной гипертензии",
        validators=[DataRequired()],
        choices=[
            ("1", "1"),
            ("2","2"),
            ("3", "3"),
            ("Нет", "Нет")]
    )
    dyslipidemia = SelectField(
        "Дислипидемия",
        validators=[DataRequired()],
        choices=[
            ("Да", "Да"),
            ("Нет", "Нет")]
    )
    heredity = SelectField(
        "Наследственность по ожирению и Сахарному Диабету 2 типа",
        validators=[DataRequired()],
        choices=[
            ("Да", "Да"),
            ("Нет", "Нет")]
    )
    complications_history = SelectField(
        "Осложнения Сахарного диабета 2 типа в анамнезе",
        validators=[DataRequired()],
        choices=[
            ("Да", "Да"),
            ("Нет", "Нет")]
    )
    gestational_diabetes = SelectField(
        "Гестационный Сахарный Диабет в анамнезе",
        validators=[DataRequired()],
        choices=[
            ("Да", "Да"),
            ("Нет", "Нет")]
    )
    X9_HbA1c_before_surgery = DecimalField(
        "Уровень гликированного гемоглобина в крови до операции",
        validators=[DataRequired(),
            NumberRange(min=4, max=60, message="Введите корректное значение")],
        places=4
    )
    Target_HbA1c_now = DecimalField(
        "Уровень гликированного гемоглобина на данный момент",
        validators=[DataRequired(), NumberRange(min=4, max=60, message="Введите корректное значение")],
        places=4
    )

    def validate(self, extra_validators):
        initial_validation = super(CalculateForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        if self.survey_date.data > datetime.now().date():
            self.survey_date.errors.append("Некорректная дата опроса!")
            return False
        
        if self.survey_date.data <= self.surgery_date.data:
            self.surgery_date.errors.append("Дата операции должна быть раньше даты опроса!")
            return False

        age = (datetime.now().date() - self.birthdate.data).days / 365
        if age < 18:
            self.birthdate.errors.append("Пациент должен быть старше 18 лет!")
            return False

        duration = (datetime.now().date() - self.surgery_date.data).days / 365
        if duration <= 4:
            self.surgery_date.errors.append("С момента проведения операции должно пройти более 4 лет!")
            return False
        
        if self.birthdate.data >= self.surgery_date.data:
            self.surgery_date.errors.append(
                "Дата рождения должна быть раньше даты операции!"
            )
            return False

        if self.surgery_date.data <= self.diagnosis_date.data:
            self.diagnosis_date.errors.append(
                "Дата выявления болезни должна быть раньше даты операции!"
            )
            return False

        if self.diagnosis_date.data <= self.birthdate.data:
            self.birthdate.errors.append(
                "Дата рождения должна быть раньше даты выявления болезни!"
            )
            return False
        return True
