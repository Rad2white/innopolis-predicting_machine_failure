from flask import Flask, request, redirect, render_template, send_from_directory, jsonify
import pandas as pd
from db.db import *
from joblib import load
import datetime
import os

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
XGB_model_loaded = load('model/XGB_model.joblib')

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/static')
def static_files(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

@app.route('/result_page', methods=['POST'])
def result():
    try:
        # Реквест данных из формы ввода
        type_frais = int(request.form['type_frais']) #тип станка
        air_temp = float(request.form['air_temp'].replace(",", ".")) #температура воздуха
        proc_temp = float(request.form['proc_temp'].replace(",", ".")) #температура процесса
        rotation_speed = int(request.form['rotation_speed']) #скорость вращения инструмента
        torque = float(request.form['torque'].replace(",", ".")) #крутящий момент
        tool_wear = int(request.form['tool_wear']) #износ иснтрумента

        result_string, probability = process_data(type_frais, air_temp, proc_temp, rotation_speed, torque, tool_wear)
        # Запись в БД
        db_manager = DbManager('db\\db.db')
        x = datetime.datetime.now()
        date, time = str(x).split(' ')
        db_manager.insert_history(date, time)
        db_manager.result_history(type_frais, air_temp, proc_temp, rotation_speed, torque, tool_wear, result_string)

        # Результат в формате JSON для возвращения в контейнер результатов
        return jsonify({'result': result_string, 'prob': probability})

    except ValueError as e:
        error_message = "Вы неверно ввели данные. Пожалуйста, повторите ввод."
        return jsonify({'error': error_message})
    
#функция для формирования датафрейма и прогнозирования с помощью загруженной модели    
def process_data(type_frais,air_temp,proc_temp,rotation_speed,torque,tool_wear):
    #формируем тестовый датафрейм
    list_tuples =[[type_frais,air_temp,proc_temp,rotation_speed,torque,tool_wear]]
    X_test = pd.DataFrame(list_tuples, columns=['type', 'airtemperature', 'processtemperature', 
                                                'rotationalspeedrpm', 'torquenm', 'toolwearmin'])
    #прогноз и ответ 
    y_pred_dec = XGB_model_loaded.predict(X_test).tolist()[0]
    if y_pred_dec == 1:
        result_str = "подвержен поломке"
    else:
        result_str = "работает в оптимальном режиме"
    probability_proba = XGB_model_loaded.predict_proba(X_test)
    probability = round(probability_proba.tolist()[0][0]*100,2) #вероятность
    return result_str, probability

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')