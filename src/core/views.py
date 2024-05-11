from flask import render_template, request
from flask_login import login_required
from flask import Blueprint, render_template, request, session
from fileinput import filename
import pandas as pd
import os
from werkzeug.utils import secure_filename
from src import app
from flask import send_file
import csv

core_bp = Blueprint("core", __name__)


@core_bp.route("/home")
@login_required
def home():
    return render_template("core/index.html")


#@core_bp.route('/home', methods=['GET', 'POST'])
#@login_required
def uploadFile():
    if request.method == 'POST':
      # upload file flask
        f = request.files.get('file')
 
        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)
 
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            data_filename))
 
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'],
                     data_filename)
 
        return render_template('core/index.html')
    return render_template("core/index.html")
 
 
@core_bp.route('/show_data')
@login_required
def showData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv
    uploaded_df = pd.read_csv(data_file_path,
                              encoding='UTF-8',delimiter=';')
    # Converting to html Table
    uploaded_df_html = uploaded_df.to_html()
    return render_template('core/show_csv_data.html',
                           data_var=uploaded_df_html)

@core_bp.route('/home', methods=['GET', 'POST'])
@login_required
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
                "Уровень гликированного гемоглобина в крови на момент опроса"
            ]
        )
    return send_file(
        f"../{filename}",
        mimetype="text/csv",
        download_name="Tempate.csv",
        as_attachment=True
    )