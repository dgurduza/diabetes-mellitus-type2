from flask_login import login_required
from flask import Blueprint, render_template, request, session, flash, send_file, jsonify
from fileinput import filename
from werkzeug.utils import secure_filename
from src import app,db
from src.calculator.models import Patient
from src.calculator.regression import Regression
from datetime import datetime
import pandas as pd
import os
import csv
import pickle
import uuid
import json
from src.calculator.views import calculate_age_at_operation,calculate_bmi,calculate_post_operation_duration,calculate_illness_duration

core_bp = Blueprint("core", __name__)

def get_model():
    deserialize_array = None
    with open('src/statistics/model.pkl', 'rb') as f:
        deserialize_array = pickle.load(f)
        data = Regression(deserialize_array)
    return data

Data = get_model()
regression = Data.model
groups_expected_val = Data.groups_expected_val

@core_bp.route("/home")
@login_required
def home():
    return render_template("core/index.html")

@core_bp.route("/analitics")
@login_required
def get_analitics():
    return render_template("core/analitics.html")


@core_bp.route("/view_patients")
@login_required
def get_table():
    data=db.session.query(Patient).all()
    print(json.dumps([record.serialize for record in data],ensure_ascii=False))
    return render_template("core/view_patients.html",result=json.dumps([record.serialize for record in data],ensure_ascii=False))


@core_bp.route('/home', methods=['GET', 'POST'])
@login_required
def uploadFile():
    if request.method == 'POST':
        #try:
            # upload file flask
            f = request.files.get('file')
 
            # Extracting uploaded file name
            data_filename = secure_filename(f.filename)
 
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                data_filename))
 
            session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'],
                         data_filename)
            nums = None
            with open(session.get('uploaded_data_file_path', None), 'r') as f:
                nums = f.read().splitlines()
        
            check_arr = nums[0].split(',')
            count = 0
            if nums[0] == 'Дата опроса,ФИО,Дата рождения (дд.мм.ГГГГ),Пол,Рост (М),Масса тела при рождении (КГ),Масса тела на момент опроса (КГ),Дата выявления СД2,Тип операции,Дата операции (дд.мм.ГГГГ),Максимальная масса тела до операции(КГ),Масса тела перед операцией(КГ),Минимальная масса тела после операции(КГ),Сахароснижающая терапия до операции,Уровень гликированного гемоглобина в крови до операции (%),Степень Артериальной гипертензии,Дислипидемия,Наследственность по ожирению и Сахарному Диабету 2 типа,Осложнения Сахарного диабета 2 типа в анамнезе,Гестационный Сахарный Диабет в анамнезе,Уровень гликированного гемоглобина в крови на момент опроса (%)':
                nums.pop(0)
                for i in nums:
                    data = i.split(sep=',')
                    if db.session.query(Patient).filter(Patient.survey_date == datetime.strptime(data[0], "%d.%m.%Y"),
                                            Patient.fullname == data[1],
                                            Patient.birthdate == datetime.strptime(data[2], "%d.%m.%Y"),
                                            Patient.gender == data[3],
                                            Patient.X6_birth_weight == float(data[5]),
                                            Patient.diagnosis_date == datetime.strptime(data[7], "%d.%m.%Y"),
                                            Patient.surgery_type == data[8]).count() != 0 or len(data) != len(check_arr):
                        break

                    #TODO: Подумать над UUID
                    if db.session.query(Patient).filter(Patient.fullname == data[1],
                                            Patient.birthdate == datetime.strptime(data[2], "%d.%m.%Y"),
                                            Patient.gender == data[3],
                                            Patient.X6_birth_weight == float(data[5]),
                                            Patient.diagnosis_date == datetime.strptime(data[7], "%d.%m.%Y"),
                                            Patient.surgery_type == data[8]).count() != 0:
                        patient = db.session.query(Patient).get([data[1],
                                                        datetime.strptime(data[2], "%d.%m.%Y"),
                                                        data[3],
                                                        float(data[5]),
                                                        datetime.strptime(data[7], "%d.%m.%Y"),
                                                        data[8]])
                
                        get_pat_uuid = patient.pat_uuid
                    else:
                        get_pat_uuid = str(uuid.uuid4())

                    
                    patient = Patient(
                        pat_uuid = get_pat_uuid,
                        survey_date=datetime.strptime(data[0], "%d.%m.%Y"),
                        fullname=data[1],
                        birthdate=datetime.strptime(data[2], "%d.%m.%Y"),
                        gender=data[3],
                        height=float(data[4]),
                        X6_birth_weight=float(data[5]),
                        weight=float(data[6]),
                        diagnosis_date=datetime.strptime(data[7], "%d.%m.%Y"),
                        surgery_type=data[8],
                        surgery_date=datetime.strptime(data[9], "%d.%m.%Y"),
                        max_weight_before_surgery=float(data[10]),
                        weight_before_surgery=float(data[11]),
                        min_weight_after_surgery=float(data[12]),
                        therapy_before_surgery=data[13],
                        X9_HbA1c_before_surgery=float(data[14]),
                        arterial_hypertension_degree = data[15],
                        dyslipidemia = data[16],
                        heredity = data[17],
                        complications_history = data[18],
                        gestational_diabetes = data[19],
                        X1_age_at_surgery= calculate_age_at_operation(datetime.strptime(data[2], "%d.%m.%Y"),datetime.strptime(data[9], "%d.%m.%Y")),
                        X2_period_after_surgery= calculate_post_operation_duration(datetime.strptime(data[0], "%d.%m.%Y"),datetime.strptime(data[9], "%d.%m.%Y")),
                        X3_max_BMI_before_surgery= calculate_bmi(float(data[10]),float(data[4])),
                        X4_BMI_before_surgery= calculate_bmi(float(data[11]),float(data[4])),
                        X5_BMI_at_survey= calculate_bmi(float(data[6]),float(data[4])),
                        X7_min_BMI_after_surgery= calculate_bmi(float(data[12]),float(data[4])),
                        X8_illness_duration=calculate_illness_duration(datetime.strptime(data[9], "%d.%m.%Y"),datetime.strptime(data[7], "%d.%m.%Y")),
                        Target_HbA1c_now=float(data[20])
                    )
            
                
                    group = ';'.join([patient.gender,patient.surgery_type,patient.therapy_before_surgery])
                    X = pd.DataFrame({'X1': [patient.X1_age_at_surgery], 'X2': [patient.X2_period_after_surgery], 
                                'X3': [patient.X3_max_BMI_before_surgery],'X4': [patient.X4_BMI_before_surgery], 
                                'X5': [patient.X5_BMI_at_survey], 'X6': [float(patient.X6_birth_weight*1000)], 
                                'X7': [patient.X7_min_BMI_after_surgery], 'X8': [patient.X8_illness_duration], 
                                'X9': [float(patient.X9_HbA1c_before_surgery/100)],'const':[1]})
            
                    if group in groups_expected_val:
                        result_reg = regression.predict(X) + groups_expected_val[group][0]
                    else:
                        result_reg = regression.predict(X) + groups_expected_val['M_data']
                
                    patient.HbA1c_predicted = result_reg * 100
                    count = count + 1
                    db.session.add(patient)
                    db.session.commit()

        #except Exception as e:
        #        db.session.rollback()
        #        flash(f"Непредвиденная ошибка при сохранении данных: {e}", "danger")

    flash(f"Загружено: {count} пациентов", "success")
    return render_template("core/index.html")

 
 
@core_bp.route('/show_data')
@login_required
def showData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv
    uploaded_df = pd.read_csv(data_file_path,
                              encoding='UTF-8',delimiter='')
    # Converting to html Table
    with open(data_file_path, 'r') as f:
        nums = f.read().splitlines()
    uploaded_df_html = uploaded_df.to_html()
    return render_template('core/show_csv_data.html',
                           data_var=uploaded_df_html)

# ГОТОВО
#@core_bp.route('/home', methods=['GET', 'POST'])
#@login_required
def get_template():
    filename = "template.csv"
    with open(filename, "w", newline="") as unloadable_table:
        csvwriter = csv.writer(unloadable_table)
        csvwriter.writerow(
            [
                "Дата опроса",
                "ФИО",
                "Дата рождения (дд.мм.ГГГГ)",
                "Пол",
                "Рост (М)",
                "Масса тела при рождении (КГ)",
                "Масса тела на момент опроса (КГ)",
                "Дата выявления СД2",
                "Тип операции",
                "Дата операции (дд.мм.ГГГГ)",
                "Максимальная масса тела до операции(КГ)",
                "Масса тела перед операцией(КГ)",
                "Минимальная масса тела после операции(КГ)",
                "Сахароснижающая терапия до операции",
                "Уровень гликированного гемоглобина в крови до операции (%)",
                "Степень Артериальной гипертензии",
                "Дислипидемия",
                "Наследственность по ожирению и Сахарному Диабету 2 типа",
                "Осложнения Сахарного диабета 2 типа в анамнезе",
                "Гестационный Сахарный Диабет в анамнезе",
                "Уровень гликированного гемоглобина в крови на момент опроса (%)"
            ]
        )
    return send_file(
        f"../{filename}",
        mimetype="text/csv",
        download_name="Tempate.csv",
        as_attachment=True
    )