import pickle
from pathlib import Path
from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

MODEL_DIR = Path(__file__).resolve().parent / "models"
with (MODEL_DIR / "ridge.pkl").open("rb") as model_file:
    ridge_model = pickle.load(model_file)
with (MODEL_DIR / "scaler.pkl").open("rb") as scaler_file:
    standard_scaler = pickle.load(scaler_file)


application = Flask(__name__)
app = application


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == "POST":
        day=float(request.form.get('day'))
        month=float(request.form.get('month'))
        year=float(request.form.get('year'))
        Temperature=float(request.form.get('Temperature'))
        RH=float(request.form.get('RH'))
        Ws=float(request.form.get('Ws'))
        Rain=float(request.form.get('Rain'))
        FFMC=float(request.form.get('FFMC'))
        DMC=float(request.form.get('DMC'))
        ISI=float(request.form.get('ISI'))
        Classes=float(request.form.get('Classes'))
        Region=float(request.form.get('Region'))

        input_data=pd.DataFrame(
            [[day,month,year,Temperature,RH,Ws,Rain,FFMC,DMC,ISI,Classes,Region]],
            columns=standard_scaler.feature_names_in_
        )
        new_data_scaled=standard_scaler.transform(input_data)
        result=ridge_model.predict(new_data_scaled)

        return render_template('home.html',results=result[0])
    else:
        return render_template('home.html')
if __name__=="__main__":
    app.run(host="0.0.0.0")
