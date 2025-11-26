import logging
import os
import sqlite3
import datetime
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
from pathlib import Path

# --- Configuration ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = BASE_DIR / "model" / "health_model.pkl"
DB_PATH = BASE_DIR / "user_logs.db"

# --- Load Resources ---
FOOD_DB = []
MODEL = None
SCALER = None

def load_resources():
    global FOOD_DB, MODEL, SCALER
    
    # 1. Load Food Data
    food_file = DATA_DIR / "cleaned_foods.csv"
    if food_file.exists():
        try:
            df_food = pd.read_csv(food_file)
            FOOD_DB = df_food.to_dict('records')
            logger.info(f"✅ Loaded {len(FOOD_DB)} food items.")
        except Exception as e:
            logger.error(f"❌ Error loading food data: {e}")
    else:
        logger.warning("⚠️ Food data file not found!")

    # 2. Load AI Model
    if MODEL_PATH.exists():
        try:
            SCALER, models = joblib.load(MODEL_PATH)
            MODEL = models
            logger.info("✅ Loaded AI Models (Diabetes, Cardio, Hypertension).")
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
    else:
        logger.warning("⚠️ Model file not found!")

def init_db():
    """Initialize SQLite database for logs."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_info TEXT,
        food_input TEXT,
        nutrition_stats TEXT,
        predictions TEXT
    )""")
    conn.commit()
    conn.close()

# --- Helper Functions ---
def find_food_in_text(text):
    """Simple keyword matching to find foods in user input."""
    text = text.lower()
    found_foods = []
    total_nutrition = {"calo": 0, "sugar": 0, "fat": 0, "protein": 0, "salt": 0}
    
    for food in FOOD_DB:
        # Check if food name appears in text
        if food['name'].lower() in text:
            found_foods.append(food)
            total_nutrition["calo"] += float(food.get('calo', 0))
            total_nutrition["sugar"] += float(food.get('sugar', 0))
            total_nutrition["fat"] += float(food.get('fat', 0))
            total_nutrition["protein"] += float(food.get('protein', 0))
            total_nutrition["salt"] += float(food.get('salt', 0))
            
    return found_foods, total_nutrition

def estimate_health_indicators(user_info, nutrition):
    """
    Heuristic function to estimate blood indicators based on profile + food.
    WARNING: This is for simulation/demo purposes only.
    """
    age = float(user_info.get('age', 30))
    bmi = float(user_info.get('bmi', 22))
    sugar_intake = nutrition['sugar']
    
    # Base values (Normal person)
    glucose = 85.0 
    hba1c = 5.0
    
    # Adjust based on BMI (Higher BMI -> Higher base glucose)
    if bmi > 25: glucose += (bmi - 25) * 2
    if bmi > 30: hba1c += 0.5
    
    # Adjust based on Age
    if age > 50: glucose += 5
    
    # Adjust based on Sugar Intake (The "Simulation" part)
    # Assume 1g sugar spikes glucose temporarily
    glucose += sugar_intake * 0.5 
    
    # Cap values to realistic ranges
    glucose = min(max(glucose, 70), 300)
    hba1c = min(max(hba1c, 4), 15)
    
    return glucose, hba1c

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/foods')
def get_foods():
    """Return list of food names for autocomplete."""
    names = [f['name'] for f in FOOD_DB]
    return jsonify(names)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        user_info = data.get('userInfo', {})
        food_text = data.get('foodText', '')
        
        # 1. Parse Food
        found_foods, nutrition = find_food_in_text(food_text)
        
        # 2. Calculate BMI
        try:
            height = float(user_info.get('height', 170)) / 100 # cm to m
            weight = float(user_info.get('weight', 65))
            bmi = round(weight / (height * height), 2)
        except:
            bmi = 22.0
            
        # 3. Estimate Medical Indicators (Simulation)
        glucose, hba1c = estimate_health_indicators({'age': user_info.get('age'), 'bmi': bmi}, nutrition)
        
        # 4. AI Prediction
        predictions = {"diabetes": 0, "cardio": 0, "hypertension": 0}
        if MODEL and SCALER:
            # Input features: ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease', 'diabetes']
            # Note: The scaler was fitted on ALL columns. We need to construct the full vector.
            # However, we are predicting hypertension/heart_disease/diabetes.
            # This creates a circular dependency if we strictly follow the training columns.
            # For the demo, we will use the specific feature subsets we trained on.
            
            # Map inputs
            gender = 1 if user_info.get('gender') == 'Male' else 0
            age = float(user_info.get('age', 30))
            smoking = int(user_info.get('smoking', 0)) # 0: never, 1: current...
            
            # Prepare Input Vector for Diabetes Model (gender, age, bmi, smoking, hba1c, glucose, hypertension, heart_disease)
            # We assume no pre-existing conditions (0, 0) for the first prediction
            input_d = np.array([[gender, age, bmi, smoking, hba1c, glucose, 0, 0]])
            
            # We need to scale this. But the scaler expects 9 columns. 
            # Workaround: Create a dummy 9-col array, scale it, then extract needed cols? 
            # Or better: Just use the raw values if the model is robust (RandomForest is scale-invariant usually, but we scaled it).
            # Let's try to reconstruct the 9-col vector with dummy targets.
            full_input = np.array([[gender, age, bmi, smoking, hba1c, glucose, 0, 0, 0]])
            scaled_input = SCALER.transform(full_input)
            
            # Extract scaled features. The order in scaler.feature_names_in_ matches all_cols
            # all_cols = ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease', 'diabetes']
            
            # Diabetes Model used: ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease']
            # Indices: 0, 1, 2, 3, 4, 5, 6, 7
            X_d = scaled_input[:, [0,1,2,3,4,5,6,7]]
            prob_d = MODEL['diabetes'].predict_proba(X_d)[0][1]
            
            # Cardio Model used: ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'diabetes']
            # Indices: 0, 1, 2, 3, 4, 5, 6, 8 (We use the predicted diabetes prob as input? Or binary? Let's use prob for smoother result)
            # Actually RF expects binary usually, but let's pass the probability as a "risk score" proxy or threshold it.
            # Let's threshold diabetes prediction for the next input
            is_diabetes = 1 if prob_d > 0.5 else 0
            
            # Re-scale with new diabetes info? No, scaler is fixed. 
            # We just construct the vector for the model.
            # Note: The scaler transform applies (x - mean) / std. It doesn't care about dependencies.
            # So we can just use the scaled values from `scaled_input` for common features, and manually scale the 'diabetes' feature?
            # Too complex. Let's just create a new full input with the predicted diabetes value.
            full_input_c = np.array([[gender, age, bmi, smoking, hba1c, glucose, 0, 0, is_diabetes]])
            scaled_input_c = SCALER.transform(full_input_c)
            X_c = scaled_input_c[:, [0,1,2,3,4,5,6,8]]
            prob_c = MODEL['cardio'].predict_proba(X_c)[0][1]
            
            # Hypertension Model used: ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'diabetes', 'heart_disease']
            # Indices: 0, 1, 2, 3, 4, 5, 8, 7
            is_cardio = 1 if prob_c > 0.5 else 0
            full_input_h = np.array([[gender, age, bmi, smoking, hba1c, glucose, 0, is_cardio, is_diabetes]])
            scaled_input_h = SCALER.transform(full_input_h)
            X_h = scaled_input_h[:, [0,1,2,3,4,5,8,7]]
            prob_h = MODEL['hypertension'].predict_proba(X_h)[0][1]
            
            predictions = {
                "diabetes": round(prob_d * 100, 1),
                "cardio": round(prob_c * 100, 1),
                "hypertension": round(prob_h * 100, 1)
            }

        # 5. Log to DB
        # (Skip for speed in this step, but structure is there)
        
        return jsonify({
            "success": True,
            "nutrition": nutrition,
            "foods": [f['name'] for f in found_foods],
            "bmi": bmi,
            "simulated_health": {"glucose": round(glucose, 1), "hba1c": round(hba1c, 1)},
            "predictions": predictions
        })

    except Exception as e:
        logger.error(f"Analysis Error: {e}")
        return jsonify({"success": False, "error": str(e)})

# --- Main ---
if __name__ == "__main__":
    load_resources()
    init_db()
    app.run(debug=True, port=5000)
