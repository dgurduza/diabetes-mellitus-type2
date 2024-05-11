from .forms import CalculateForm
from src.calculator.models import Patient, Survey
from src import db
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from src.calculator.regression import Regression
import pickle
import pandas as pd
from sqlalchemy.inspection import inspect

calculator_bp = Blueprint("calculator", __name__)

def get_model():
    deserialize_array = None
    with open('src/statistics/model.pkl', 'rb') as f:
        deserialize_array = pickle.load(f)
        data = Regression(deserialize_array)
    return data

HOME_URL = "core.home"
Data = get_model()
regression = Data.model
groups_expected_val = Data.groups_expected_val

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
    result = {}
    if form.validate_on_submit():
        try:
            if db.session.query(Patient).filter(Patient.fullname == form.fullname.data,
                                            Patient.birthdate == form.birthdate.data.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                            Patient.gender == form.gender.data,
                                            Patient.X6_birth_weight == form.X6_birth_weight.data,
                                            Patient.diagnosis_date == form.diagnosis_date.data.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                            Patient.surgery_type == form.surgery_type.data).count() == 0:
            
                patient = Patient(
                    fullname=form.fullname.data,
                    birthdate=form.birthdate.data,
                    gender=form.gender.data,
                    height=form.height.data,
                    X6_birth_weight=form.X6_birth_weight.data,
                    diagnosis_date=form.diagnosis_date.data,
                    surgery_type=form.surgery_type.data,
                    surgery_date=form.surgery_date.data,
                    max_weight_before_surgery=form.max_weight_before_surgery.data,
                    weight_before_surgery=form.weight_before_surgery.data,
                    therapy_before_surgery=form.therapy_before_surgery.data,
                    X9_HbA1c_before_surgery=form.X9_HbA1c_before_surgery.data,
                    arterial_hypertension_degree = form.arterial_hypertension_degree.data,
                    dyslipidemia = form.dyslipidemia.data,
                    heredity = form.heredity.data,
                    complications_history = form.complications_history.data,
                    gestational_diabetes = form.gestational_diabetes.data,
                    X1_age_at_surgery= calculate_age_at_operation(form.birthdate.data,form.surgery_date.data),
                    X3_max_BMI_before_surgery= calculate_bmi(form.max_weight_before_surgery.data,form.height.data),
                    X4_BMI_before_surgery= calculate_bmi(form.weight_before_surgery.data,form.height.data),
                    X8_illness_duration=calculate_illness_duration(form.surgery_date.data,form.diagnosis_date.data)
                )

                survey = Survey(UUID=patient.pat_uuid,
                                survey_date=form.survey_date.data,
                                weight=form.weight.data,
                                min_weight_after_surgery=form.min_weight_after_surgery.data,
                                X2_period_after_surgery= calculate_post_operation_duration(form.survey_date.data,form.surgery_date.data),
                                X5_BMI_at_survey= calculate_bmi(form.weight.data,form.height.data),
                                X7_min_BMI_after_surgery= calculate_bmi(form.min_weight_after_surgery.data,form.height.data),
                                Target_HbA1c_now=form.Target_HbA1c_now.data)
                db.session.add(patient)
            else:
                patient = db.session.query(Patient).get([form.fullname.data,
                                                        form.birthdate.data,
                                                        form.gender.data,
                                                        form.X6_birth_weight.data,
                                                        form.diagnosis_date.data,
                                                        form.surgery_type.data])
                survey = Survey(UUID=patient.pat_uuid,
                                survey_date=form.survey_date.data,
                                weight=form.weight.data,
                                min_weight_after_surgery=form.min_weight_after_surgery.data,
                                X2_period_after_surgery= calculate_post_operation_duration(form.survey_date.data,form.surgery_date.data),
                                X5_BMI_at_survey= calculate_bmi(form.weight.data,form.height.data),
                                X7_min_BMI_after_surgery= calculate_bmi(form.min_weight_after_surgery.data,form.height.data),
                                Target_HbA1c_now=form.Target_HbA1c_now.data)
                
            group = ';'.join([patient.gender,patient.surgery_type,patient.therapy_before_surgery])
            X = pd.DataFrame({'X1': [patient.X1_age_at_surgery], 'X2': [survey.X2_period_after_surgery], 
                                'X3': [patient.X3_max_BMI_before_surgery],'X4': [patient.X4_BMI_before_surgery], 
                                'X5': [survey.X5_BMI_at_survey], 'X6': [float(patient.X6_birth_weight*1000)], 
                                'X7': [survey.X7_min_BMI_after_surgery], 'X8': [patient.X8_illness_duration], 
                                'X9': [float(patient.X9_HbA1c_before_surgery/100)],'const':[1]})
            
            if group in groups_expected_val:
                result_reg = regression.predict(X) + groups_expected_val[group][0]
            else:
                result_reg = regression.predict(X) + groups_expected_val['M_data']
                
            survey.HbA1c_predicted = result_reg * 100
            
            db.session.add(survey)
            db.session.commit()
            result['message'] = f'Форма успешно обработана:{result_reg}'
            
        except Exception as e:
                db.session.rollback()
                flash(f"Непредвиденная ошибка при сохранении данных: {e}", "danger")
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"Ошибка в поле '{fieldName}': {err}", "danger")

    return render_template("calculator/survey.html", form=form, result=result)