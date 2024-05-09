from flask_wtf import FlaskForm
from datetime import datetime, timedelta
from wtforms import StringField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

from src.calculator.models import Patient


# TODO: Check date validation
class CalculateForm(FlaskForm):
    survey_date = DateField(
        "Дата опроса", validators=[DataRequired()], format="%d.%m.%Y"
    )
    fullname = StringField(
        "Фамилия Имя Отчество", validators=[DataRequired(), Length(min=4, max=50)]
    )
    birthdate = DateField(
        "Дата рождения", validators=[DataRequired()], format="%d.%m.%Y"
    )
    gender = SelectField(
        "Пол", validators=[DataRequired()], choices=[("Ж", "Ж"), ("М", "М")]
    )
    height = DecimalField(
        "Рост",
        validators=[
            DataRequired(),
            NumberRange(min=1.0, max=2.7, message="Введите корректное значение"),
        ],
        places=4,
    )
    X6_birth_weight = DecimalField(
        "Масса тела при рождении",
        validators=[
            DataRequired(),
            NumberRange(min=0.5, max=6, message="Введите корректное значение"),
        ],
        places=4,
    )
    weight = DecimalField(
        "Масса тела на момент опроса",
        validators=[
            DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение"),
        ],
        places=4,
    )
    diagnosis_date = DateField(
        "Дата диагностирования СД2", validators=[DataRequired()], format="%d.%m.%Y"
    )
    surgery_type = SelectField(
        "Тип операции",
        validators=[DataRequired()],
        choices=[
            ("Продольная резекция желудка", "Продольная резекция желудка"),
            ("Гастрошунтирование", "Гастрошунтирование"),
            ("Билиопанкреатическое шунтирование", "Билиопанкреатическое шунтирование"),
        ],
    )
    surgery_date = DateField(
        "Дата операции", validators=[DataRequired()], format="%d.%m.%Y"
    )
    max_weight_before_surgery = DecimalField(
        "Максимальная масса тела до операции",
        validators=[
            DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение"),
        ],
        places=4,
    )
    weight_before_surgery = DecimalField(
        "Масса тела перед операцией",
        validators=[
            DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение"),
        ],
        places=4,
    )
    min_weight_after_surgery = DecimalField(
        "Минимальная масса тела после операции",
        validators=[
            DataRequired(),
            NumberRange(min=25, max=500, message="Введите корректное значение"),
        ],
        places=4,
    )
    therapy_before_surgery = SelectField(
        "Тип сахароснижающей терапии до операции",
        validators=[DataRequired()],
        choices=[
            ("Монотерапия без инсулина", "Монотерапия без инсулина"),
            (
                "Комбинированная терапия без инсулина",
                "Комбинированная терапия без инсулина",
            ),
            ("Терапия с инсулином", "Терапия с инсулином"),
        ],
    )
    X9_HbA1c_before_surgery = DecimalField(
        "Уровень гликированного гемоглобина в крови до операции",
        validators=[
            DataRequired(),
            NumberRange(min=4, max=35, message="Введите корректное значение"),
        ],
        places=4,
    )

    def validate(self, extra_validators):
        initial_validation = super(CalculateForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        if self.survey_date.data > datetime.now():
            self.survey_date.errors.append("Введите корректную даты опроса")
            return False
        
        if self.survey_date.data <= self.surgery_date.data:
            self.surgery_date.errors.append("Введите корректные даты опроса и операции")
            return False

        age = (datetime.now() - self.birthdate.data).days / 365
        if age < 18:
            self.birthdate.errors.append("Пациент должен быть старше 18 лет")
            return False

        duration = (datetime.now() - self.surgery_date.data).days / 365
        if duration >= 4:
            self.surgery_date.errors.append("Введите корректную дату операции")
            return False
        
        if self.birthdate.data <= self.surgery_date.data:
            self.surgery_date.errors.append(
                "Введите корректные даты рождения и выявления болезни"
            )
            return False

        if self.surgery_date.data <= self.diagnosis_date.data:
            self.diagnosis_date.errors.append(
                "Введите корректные даты операции и выявления болезни"
            )
            return False

        if self.diagnosis_date.data <= self.birthdate.data:
            self.birthdate.errors.append(
                "Введите корректные даты рождения и выявления болезни"
            )
            return False
        return True
        # first_date = datetime.strptime(self.surgery_date.data, '%d.%m.%Y')
        # second_date = datetime.strptime(datetime.now(), '%d.%m.%Y')
