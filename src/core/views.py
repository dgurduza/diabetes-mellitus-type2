from flask_login import current_user, login_required, login_user, logout_user
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    send_file,
    redirect,
    url_for,
)
from fileinput import filename
from werkzeug.utils import secure_filename
from src import app, db
from src.calculator.models import Patient
from src.calculator.regression import Regression
from src.calculator.views import Data,groups_expected_val,regression
from datetime import datetime
from .forms import RegisterForm, AnaliticsForm
from src.accounts.models import User
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import csv
import pickle
import uuid
import json
from src.calculator.views import (
    calculate_age_at_operation,
    calculate_bmi,
    calculate_post_operation_duration,
    calculate_illness_duration,
)

core_bp = Blueprint("core", __name__)


def get_model(path):
    deserialize_array = None
    if len(path) == 0:
        path = "src/statistics/model.pkl"
    with open(path, "rb") as f:
        deserialize_array = pickle.load(f)
        data = Regression(deserialize_array)
    return data


Data = get_model("")
regression = Data.model
groups_expected_val = Data.groups_expected_val
cat_factor = {
    "gender": "Пол",
    "surgery_type": "Тип операции",
    "therapy_before_surgery": "Сахароснижающая терапия до операции",
    "arterial_hypertension_degree": "Степень артериальной гипертензии",
    "dyslipidemia": "Дислипидемия",
    "heredity": "Наследственность по ожирению и СД2",
    "complications_history": "Осложнения Сахарного диабета 2 типа в анамнезе",
    "gestational_diabetes": "Гестационный Сахарный Диабет в анамнезе",
}

nums_factor = {
    "X1_age_at_surgery": "Возраст на момент проведения операции",
    "X2_period_after_surgery": "Длительность периода после операции",
    "X3_max_BMI_before_surgery": "Максимальный ИМТ до операции",
    "X4_BMI_before_surgery": "ИМТ перед операцией",
    "X5_BMI_at_survey": "ИМТ на момент опроса",
    "X6_birth_weight": "Масса тела при рождении",
    "X7_min_BMI_after_surgery": "Минимальный ИМТ после операции",
    "X8_illness_duration": "Длительность СД2",
    "X9_HbA1c_before_surgery": "Уровень гликированного гемоглобина в крови до операции",
}
VERIFY_2FA_URL = "accounts.verify_two_factor_auth"


@core_bp.route("/home")
@login_required
def home():
    if current_user.is_two_factor_authenticated:
        plot = get_Y_plot()
        return render_template("core/index.html", graphJSON=plot)

    flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
    return redirect(url_for(VERIFY_2FA_URL))


def get_Y_plot():
    column_data_pred = db.session.query(Patient.HbA1c_predicted).all()
    arr_pred = [record.HbA1c_predicted for record in column_data_pred]

    column_data_Y = db.session.query(Patient.Target_HbA1c_now).all()
    arr_Y = [record.Target_HbA1c_now for record in column_data_Y]

    dataframe = pd.DataFrame({"Предсказанный Y": arr_pred, "Y": arr_Y})
    dataframe["Предсказанный Y"] = dataframe["Предсказанный Y"].astype(float)
    dataframe["index"] = dataframe.index
    fig = px.line(
        dataframe, x="index", y="Предсказанный Y", markers=True, labels={'Предсказанный Y': "Предсказанный Y"}
    )
    fig.update_traces(line_color="#147852")
    fig_Y = px.line(dataframe, x="index", y="Y", markers=True,labels={'Y': "Y"})
    fig = go.Figure(data=fig.data + fig_Y.data)
    fig.update_layout(title="График предсказанного уровня HbA1c и нынешнего уровня HbA1c пациентов",showlegend=True)
    # fig.add_scatter(x=dataframe["index"], y=dataframe["Y"], mode='lines')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@core_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin_console():
    if current_user.is_two_factor_authenticated:
        data = db.session.query(User).all()
        form = RegisterForm(request.form)
        if form.validate_on_submit():
            try:
                user = User(username=form.username.data, password=form.password.data)
                db.session.add(user)
                db.session.commit()
                data = db.session.query(User).all()
            except Exception:
                db.session.rollback()
                flash("Регистрация не удалась. Пожалуйста, попробуйте снова.", "danger")
        return render_template(
            "core/administration.html",
            form=form,
            result=json.dumps(
                [record.serialize for record in data], ensure_ascii=False
            ),
        )

    flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
    return redirect(url_for(VERIFY_2FA_URL))


@core_bp.route("/analitics", methods=["GET", "POST"])
@login_required
def get_analitics():
    if not current_user.is_two_factor_authenticated:
        flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
        return redirect(url_for(VERIFY_2FA_URL))

    form = AnaliticsForm(request.form)
    if form.validate_on_submit():
        column = form.variable.data
        plot_div = draw_plot(column)
        return render_template("core/analitics.html", form=form, graphJSON=plot_div)
    else:
        return render_template("core/analitics.html", form=form)


def draw_plot(column):
    column_data = db.session.query(getattr(Patient, column)).all()
    arr = [getattr(record, column) for record in column_data]

    if column in cat_factor:
        dataframe = pd.DataFrame({cat_factor[column]: arr})
        dataframe[cat_factor[column]] = dataframe[cat_factor[column]].astype(str)
        value_counts = dataframe[cat_factor[column]].value_counts()

        df_value_counts = pd.DataFrame(value_counts)
        df_value_counts = df_value_counts.reset_index()
        df_value_counts.columns = [cat_factor[column], "Количество"]
        fig = px.bar(df_value_counts, x=cat_factor[column], y="Количество",title=f"График подсчета дискретного фактора {cat_factor[column]}")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        column_data_Y = db.session.query(Patient.Target_HbA1c_now).all()
        arr_Y = [record.Target_HbA1c_now for record in column_data_Y]
        dataframe = pd.DataFrame({nums_factor[column]: arr, "Y": arr_Y})
        dataframe[nums_factor[column]] = dataframe[nums_factor[column]].astype(float)
        fig = px.scatter(
            dataframe,
            x=nums_factor[column],
            y="Y",
            title=f"Диаграмма рассеяния для {nums_factor[column]} и Уровня HbA1c",
        )
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@core_bp.route("/view_patients")
@login_required
def get_table():
    if current_user.is_two_factor_authenticated:
        data = db.session.query(Patient).all()
        return render_template(
            "core/view_patients.html",
            result=json.dumps(
                [record.serialize for record in data], ensure_ascii=False
            ),
        )

    flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
    return redirect(url_for(VERIFY_2FA_URL))


@core_bp.route("/home", methods=["GET", "POST"])
@login_required
def uploadFile():
    if current_user.is_two_factor_authenticated:
        if request.method == "POST":
            count = 0
            try:
                f = request.files.get("file")
                data_filename = secure_filename(f.filename)

                if len(data_filename) == 0:
                    flash(f"Выберите файл загрузки!", "danger")
                    plot = get_Y_plot()
                    return render_template("core/index.html", graphJSON=plot)
                elif data_filename.find(".pkl"):
                    set_model(f,data_filename)
                    plot = get_Y_plot()
                    return render_template("core/index.html", graphJSON=plot)
                
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], data_filename))
                session["uploaded_data_file_path"] = os.path.join(
                    app.config["UPLOAD_FOLDER"], data_filename
                )
                nums = None
                with open(session.get("uploaded_data_file_path", None), "r") as f:
                    nums = f.read().splitlines()

                check_arr = nums[0].split(",")
                if (
                    nums[0]
                    == "Дата опроса,ФИО,Дата рождения (дд.мм.ГГГГ),Пол,Рост (М),Масса тела при рождении (КГ),Масса тела на момент опроса (КГ),Дата выявления СД2,Тип операции,Дата операции (дд.мм.ГГГГ),Максимальная масса тела до операции(КГ),Масса тела перед операцией(КГ),Минимальная масса тела после операции(КГ),Сахароснижающая терапия до операции,Уровень гликированного гемоглобина в крови до операции (%),Степень Артериальной гипертензии,Дислипидемия,Наследственность по ожирению и Сахарному Диабету 2 типа,Осложнения Сахарного диабета 2 типа в анамнезе,Гестационный Сахарный Диабет в анамнезе,Уровень гликированного гемоглобина в крови на момент опроса (%)"
                ):
                    nums.pop(0)
                    for i in nums:
                        data = i.split(sep=",")
                        if db.session.query(Patient).filter(
                            Patient.survey_date
                            == datetime.strptime(data[0], "%d.%m.%Y"),
                            Patient.fullname == data[1],
                            Patient.birthdate == datetime.strptime(data[2], "%d.%m.%Y"),
                            Patient.gender == data[3],
                            Patient.X6_birth_weight == float(data[5]),
                            Patient.diagnosis_date
                            == datetime.strptime(data[7], "%d.%m.%Y"),
                            Patient.surgery_type == data[8],
                        ).count() != 0 or len(data) != len(check_arr):
                            break

                        get_pat_uuid = str(uuid.uuid4())
                        patient = Patient(
                            pat_uuid=get_pat_uuid,
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
                            arterial_hypertension_degree=data[15],
                            dyslipidemia=data[16],
                            heredity=data[17],
                            complications_history=data[18],
                            gestational_diabetes=data[19],
                            X1_age_at_surgery=calculate_age_at_operation(
                                datetime.strptime(data[2], "%d.%m.%Y"),
                                datetime.strptime(data[9], "%d.%m.%Y"),
                            ),
                            X2_period_after_surgery=calculate_post_operation_duration(
                                datetime.strptime(data[0], "%d.%m.%Y"),
                                datetime.strptime(data[9], "%d.%m.%Y"),
                            ),
                            X3_max_BMI_before_surgery=calculate_bmi(
                                float(data[10]), float(data[4])
                            ),
                            X4_BMI_before_surgery=calculate_bmi(
                                float(data[11]), float(data[4])
                            ),
                            X5_BMI_at_survey=calculate_bmi(
                                float(data[6]), float(data[4])
                            ),
                            X7_min_BMI_after_surgery=calculate_bmi(
                                float(data[12]), float(data[4])
                            ),
                            X8_illness_duration=calculate_illness_duration(
                                datetime.strptime(data[9], "%d.%m.%Y"),
                                datetime.strptime(data[7], "%d.%m.%Y"),
                            ),
                            Target_HbA1c_now=float(data[20]),
                        )

                        group = ";".join(
                            [
                                patient.gender,
                                patient.surgery_type,
                                patient.therapy_before_surgery,
                            ]
                        )
                        X = pd.DataFrame(
                            {
                                "X1": [patient.X1_age_at_surgery],
                                "X2": [patient.X2_period_after_surgery],
                                "X3": [patient.X3_max_BMI_before_surgery],
                                "X4": [patient.X4_BMI_before_surgery],
                                "X5": [patient.X5_BMI_at_survey],
                                "X6": [float(patient.X6_birth_weight * 1000)],
                                "X7": [patient.X7_min_BMI_after_surgery],
                                "X8": [patient.X8_illness_duration],
                                "X9": [float(patient.X9_HbA1c_before_surgery / 100)],
                                "const": [1],
                            }
                        )

                        if group in groups_expected_val:
                            result_reg = (
                                regression.predict(X) + groups_expected_val[group][0]
                            )
                        else:
                            result_reg = (
                                regression.predict(X) + groups_expected_val["M_data"]
                            )

                        patient.HbA1c_predicted = result_reg * 100
                        count = count + 1
                        db.session.add(patient)
                        db.session.commit()

            except Exception as e:
                db.session.rollback()
                flash(f"Непредвиденная ошибка: {e}", "danger")
                plot = get_Y_plot()
                return render_template("core/index.html", graphJSON=plot)

        flash(f"Загружено: {count} пациентов", "success")
        plot = get_Y_plot()
        return render_template("core/index.html", graphJSON=plot)

    flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
    return redirect(url_for(VERIFY_2FA_URL))


@core_bp.route("/template", methods=["GET", "POST"])
@login_required
def get_template():
    if current_user.is_two_factor_authenticated:
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
                    "Уровень гликированного гемоглобина в крови на момент опроса (%)",
                ]
            )
        return send_file(
            f"../{filename}",
            mimetype="text/csv",
            download_name="Tempate.csv",
            as_attachment=True,
        )
    flash("Вы не ввели OTP код. Пожалуйста, введите код.", "info")
    return redirect(url_for(VERIFY_2FA_URL))


def set_model(f, data_filename):
            try:
                print(data_filename)
                
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], data_filename))
                session["uploaded_data_file_path"] = os.path.join(
                    app.config["UPLOAD_FOLDER"], data_filename
                )

                path = os.path.join(
                    app.config["UPLOAD_FOLDER"], data_filename
                )
                print(path)
                
                Data = get_model(path)
                regression = Data.model
                groups_expected_val = Data.model
                flash(f"Модель обновлена", "info")

            except Exception as e:
                db.session.rollback()
                flash(f"Непредвиденная ошибка: 1{e}", "danger")
