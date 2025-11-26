
from flask import Flask, render_template, request, jsonify
import json, os, sqlite3, datetime, joblib, numpy as np
from pathlib import Path

app = Flask(__name__)
BASE = Path(__file__).resolve().parent
DATA = BASE/"data"/"foods_vn.json"
MODEL = BASE/"model"/"health_model.pkl"
DB = BASE/"user_logs.db"

LIMITS = {"sugar":25,"salt":5,"fat":30,"milk":200,"alcohol":200}
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, raw TEXT, sugar REAL, salt REAL, fat REAL, milk REAL, alcohol REAL,
        risk_d REAL, risk_o REAL, risk_c REAL)""")
    conn.commit(); conn.close()

def load_foods():
    with open(DATA, encoding='utf-8') as f:
        return json.load(f)

USE_ML=False
if MODEL.exists():
    try:
        scaler, md, mo = joblib.load(str(MODEL))
        USE_ML=True
    except: pass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze_text', methods=['POST'])
def analyze():
    t = request.json.get('text','').lower()
    foods = load_foods()
    totals={"sugar":0,"salt":0,"fat":0,"milk":0,"alcohol":0}
    for f in foods:
        if f["name"].lower() in t:
            totals["sugar"]+=f["sugar"]
            totals["salt"]+=f["salt"]
            totals["fat"]+=f["fat"]
            totals["milk"]+=f["milk"]
            totals["alcohol"]+=f["alcohol"]
    if USE_ML:
        X = np.array([[totals["sugar"],totals["salt"],totals["fat"],totals["milk"],totals["alcohol"],2000]])
        Xs = scaler.transform(X)
        d = md.predict_proba(Xs)[0][1]
        o = mo.predict_proba(Xs)[0][1]
        c = 0.5*d+0.5*o
    else:
        d=o=c=0.1
    risks = {"diabetes":round(d*100,1),"obesity":round(o*100,1),"cardio":round(c*100,1)}
    warnings=[]
    if totals["sugar"]>LIMITS["sugar"]: warnings.append("⚠️ Lượng đường vượt khuyến nghị WHO")
    if totals["salt"]>LIMITS["salt"]: warnings.append("⚠️ Lượng muối cao")
    return jsonify({"risks":risks,"warnings":warnings})

if __name__=="__main__":
    init_db(); app.run(debug=True)
