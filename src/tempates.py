from flask import send_file
from src import db
from datetime import datetime
import csv

# TODO: Think about sending by filters
# Send to front file with patients
#@app.route("/download/<filename>")
def download():
    if not filter:
        patients = db.session.query(patients).all()
    else:
        patients = db.session.query(patients).filter()
    filename = f"patients_{datetime.now()}.csv"
    with open(filename, "w", newline="") as unloadable_table:
        csvwriter = csv.writer(unloadable_table, delimeter=",")
        csvwriter.writerow(
            [
                "Дата опроса",
                "ФИО",
                "Дата рождения",
                "Пол",
                "Рост (М)",
                "Масса тела при рождении (КГ)",
                "Масса тела на момент опроса (КГ)",
                "Дата выявления СД2",
                "Тип операции",
                "Дата операции",
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
                
                "Возраст на момент проведения операции (Лет)",
                "Длительность периода после операции",
                "Максимальный ИМТ до операции (КГ/М^2)",
                "ИМТ перед операцией  (КГ/М^2)",
                "ИМТ на момент опроса",
                "Минимальный ИМТ после операции",
                "Длительность СД2",
                "Уровень гликированного гемоглобина в крови (%)"
            ]
        )
        for pat in patients:
            csvwriter.writerow(
                [
                    pat.survey_date,
                    pat.fullname,
                    pat.birthdate,
                    pat.gender,
                    pat.height,
                    pat.X6_birth_weight,
                    pat.weight,
                    pat.diagnosis_date,
                    pat.surgery_type,
                    pat.surgery_date,
                    pat.max_weight_before_surgery,
                    pat.weight_before_surgery,
                    pat.min_weight_after_surgery,
                    pat.therapy_before_surgery,
                    pat.X9_HbA1c_before_surgery,

                    pat.arterial_hypertension_degree,
                    pat.dyslipidemia,
                    pat.heredity,
                    pat.complications_history,
                    pat.gestational_diabetes,

                    pat.X1_age_at_surgery,
                    pat.X2_period_after_surgery,
                    pat.X3_max_BMI_before_surgery,
                    pat.X4_BMI_before_surgery,
                    pat.X5_BMI_at_survey,
                    pat.X7_min_BMI_after_surgery,
                    pat.X8_illness_duration,
                    pat.Target_HbA1c_now
                ]
            )
    return send_file(
        f"../{filename}",
        mimetype="text/csv",
        download_name="Patients.csv",
        as_attachment=True
    )

#get template for csv
def get_template():
    filename = "template.csv"
    with open(filename, "w", newline="") as unloadable_table:
        csvwriter = csv.writer(unloadable_table, delimeter=",")
        csvwriter.writerow(
            [
                "Дата опроса",
                "ФИО",
                "Дата рождения",
                "Пол",
                "Рост (М)",
                "Масса тела при рождении (КГ)",
                "Масса тела на момент опроса (КГ)",
                "Дата выявления СД2",
                "Тип операции",
                "Дата операции",
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
                "Уровень гликированного гемоглобина в крови"
            ]
        )
    return send_file(
        f"../{filename}",
        mimetype="text/csv",
        download_name="Tempate.csv",
        as_attachment=True
    )

# TODO: Write this method
#Upload data to db from csv
#def upload():
    