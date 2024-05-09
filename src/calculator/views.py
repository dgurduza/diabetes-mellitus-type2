from .forms import CalculateForm
from src.calculator.models import Patient
from src import db
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
#from src import reg_model

calculator_bp = Blueprint("calculator", __name__)

HOME_URL = "core.home"
#regression = reg_model.model
#groups_expected_val = reg_model.groups_expected_val

def calculate_age_at_operation(birthdate, operation_date):
    return (operation_date - birthdate).days / 365


def calculate_post_operation_duration(survey_date, operation_date):
    return (survey_date - operation_date).days / 365


def calculate_bmi(weight, height):
    height = float(height)
    weight = float(weight)
    return weight / (height ** 2)


def calculate_illness_duration(operation_date, diagnosis_date):
    return (operation_date - diagnosis_date).days / 365

@calculator_bp.route("/", methods=["GET", "POST"])
def calculate():
    form = CalculateForm(request.form)
    if form.validate_on_submit():
        try:
            patient = Patient(
                survey_date=form.survey_date.data,
                fullname=form.fullname.data,
                birthdate=form.birthdate.data,
                gender=form.gender.data,
                height=form.height.data,
                X6_birth_weight=form.X6_birth_weight.data,
                weight=form.weight.data,
                diagnosis_date=form.diagnosis_date.data,
                surgery_type=form.surgery_type.data,
                surgery_date=form.surgery_date.data,
                max_weight_before_surgery=form.max_weight_before_surgery.data,
                weight_before_surgery=form.weight_before_surgery.data,
                min_weight_after_surgery=form.min_weight_after_surgery.data,
                therapy_before_surgery=form.therapy_before_surgery.data,
                X9_HbA1c_before_surgery=form.X9_HbA1c_before_surgery.data,
                X1_age_at_surgery= calculate_age_at_operation(form.birthdate.data,form.surgery_date.data),
                X2_period_after_surgery= calculate_post_operation_duration(form.survey_date.data,form.surgery_date.data),
                X3_max_BMI_before_surgery= calculate_bmi(form.max_weight_before_surgery.data,form.height.data),
                X4_BMI_before_surgery= calculate_bmi(form.weight_before_surgery.data,form.height.data),
                X5_BMI_at_survey= calculate_bmi(form.weight.data,form.height.data),
                X7_min_BMI_after_surgery= calculate_bmi(form.min_weight_after_surgery.data,form.height.data),
                X8_illness_duration=calculate_illness_duration(form.surgery_date.data,form.diagnosis_date.data),
                Target_HbA1c_now=form.Target_HbA1c_now.data
            )
            db.session.add(patient)
            db.session.commit()

            return redirect(url_for(HOME_URL))
        except Exception:
            db.session.rollback()
            flash("Непредвиденная ошибка2", "danger")

    # TODO: Update html template path
    flash("Непредвиденная ошибка3", "danger")
    return render_template("calculator/survey.html", form=form)
