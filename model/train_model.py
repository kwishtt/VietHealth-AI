import pandas as pd
import numpy as np
import joblib
import os
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Cấu hình Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed_diabetes.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'health_model.pkl')

def train():
    """Huấn luyện 3 mô hình: Diabetes, Heart Disease, Obesity từ dữ liệu thật."""
    
    if not os.path.exists(DATA_PATH):
        logger.error(f"❌ Không tìm thấy file dữ liệu: {DATA_PATH}")
        return

    logger.info("🔄 Đang tải dữ liệu...")
    df = pd.read_csv(DATA_PATH)
    
    # --- 1. Chuẩn bị dữ liệu ---
    # Features chung: gender, age, smoking_history
    # Các chỉ số sức khỏe: bmi, HbA1c_level, blood_glucose_level, hypertension, heart_disease, diabetes
    
    # Để đơn giản hóa cho App, ta sẽ dùng chung một tập features đầu vào cho cả 3 model
    # Input từ App dự kiến: Gender, Age, BMI, Smoking, Glucose (ước lượng từ đường), HbA1c (ước lượng)
    feature_cols = ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease']
    
    # Xử lý dữ liệu cho từng model
    # Model Diabetes: Target = diabetes
    X_d = df[['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease']]
    y_d = df['diabetes']
    
    # Model Heart Disease: Target = heart_disease
    # Khi dự đoán tim mạch, ta dùng diabetes làm feature
    X_c = df[['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'diabetes']]
    y_c = df['heart_disease']
    
    # Model Obesity: Target = (BMI >= 30)
    # Thực tế BMI là input, nhưng để có model thứ 3 như yêu cầu, ta sẽ train nó dự đoán "Nguy cơ béo phì tiềm ẩn"
    # dựa trên các yếu tố khác (hoặc ta có thể train model dự đoán Hypertension - Huyết áp cao)
    # Ở đây em sẽ chọn train model dự đoán Hypertension (Huyết áp) vì nó hợp lý hơn (ăn mặn -> huyết áp cao)
    # Target = hypertension
    X_h = df[['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'diabetes', 'heart_disease']]
    y_h = df['hypertension']

    # --- 2. Huấn luyện ---
    
    # Scaler (Chuẩn hóa dữ liệu)
    # Ta fit scaler trên tập features đầy đủ nhất để dùng chung
    scaler = StandardScaler()
    # Fit trên tập hợp tất cả các cột có thể xuất hiện
    all_cols = ['gender', 'age', 'bmi', 'smoking_history', 'HbA1c_level', 'blood_glucose_level', 'hypertension', 'heart_disease', 'diabetes']
    scaler.fit(df[all_cols]) 
    
    models = {}
    
    # Train Diabetes Model
    logger.info("🤖 Đang train Model Diabetes...")
    X_train, X_test, y_train, y_test = train_test_split(X_d, y_d, test_size=0.2, random_state=42)
    md = RandomForestClassifier(n_estimators=100, random_state=42)
    md.fit(X_train, y_train)
    logger.info(f"   ✅ Diabetes Accuracy: {accuracy_score(y_test, md.predict(X_test)):.4f}")
    models['diabetes'] = md

    # Train Heart Disease Model
    logger.info("❤️ Đang train Model Heart Disease...")
    X_train, X_test, y_train, y_test = train_test_split(X_c, y_c, test_size=0.2, random_state=42)
    mc = RandomForestClassifier(n_estimators=100, random_state=42)
    mc.fit(X_train, y_train)
    logger.info(f"   ✅ Heart Disease Accuracy: {accuracy_score(y_test, mc.predict(X_test)):.4f}")
    models['cardio'] = mc
    
    # Train Hypertension Model (Thay cho Obesity vì Obesity tính bằng BMI rồi)
    logger.info("🩸 Đang train Model Hypertension (Huyết áp)...")
    X_train, X_test, y_train, y_test = train_test_split(X_h, y_h, test_size=0.2, random_state=42)
    mh = RandomForestClassifier(n_estimators=100, random_state=42)
    mh.fit(X_train, y_train)
    logger.info(f"   ✅ Hypertension Accuracy: {accuracy_score(y_test, mh.predict(X_test)):.4f}")
    models['hypertension'] = mh

    # --- 3. Lưu Model ---
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump((scaler, models), MODEL_PATH)
    logger.info(f"💾 Đã lưu toàn bộ model tại: {MODEL_PATH}")

if __name__ == "__main__":
    train()
