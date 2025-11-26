import pandas as pd
import os

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

FOOD_FILE = os.path.join(DATA_DIR, 'cac_mon_an.csv')
DIABETES_FILE = os.path.join(DATA_DIR, 'diabetes_prediction_dataset.csv')

OUTPUT_FOOD = os.path.join(DATA_DIR, 'cleaned_foods.csv')
OUTPUT_DIABETES = os.path.join(DATA_DIR, 'processed_diabetes.csv')

def clean_food_data():
    """Xử lý dữ liệu món ăn: Đổi tên cột, thêm cột thiếu, làm sạch."""
    print("🔄 Đang xử lý dữ liệu món ăn...")
    if not os.path.exists(FOOD_FILE):
        print(f"❌ Không tìm thấy file: {FOOD_FILE}")
        return

    df = pd.read_csv(FOOD_FILE)
    
    # 1. Chọn và đổi tên các cột cần thiết
    # File mới: dish,unit,calo,lipid,carbohydrate,protein,fiber
    # Cần map sang: name, calo, sugar, fat, salt (và các cột khác nếu muốn giữ)
    
    # Giữ lại các cột quan trọng
    df = df[['dish', 'calo', 'carbohydrate', 'lipid', 'protein']]
    df.columns = ['name', 'calo', 'sugar', 'fat', 'protein']
    
    # 2. Xóa dữ liệu trùng lặp
    df = df.drop_duplicates()
    
    # 3. Điền giá trị thiếu
    df = df.fillna(0)
    
    # 4. Thêm các cột còn thiếu (Milk, Alcohol, Salt)
    # Salt không có trong file mới, ta ước lượng hoặc để 0
    
    def estimate_salt(row):
        name = str(row['name']).lower()
        # Món mặn, kho, nước mắm...
        if any(x in name for x in ['kho', 'mắm', 'muối', 'rang', 'rim', 'canh', 'phở', 'bún', 'mì']):
            return 500.0 # Giả định 500mg muối
        return 50.0 # Mặc định ít muối

    def estimate_milk(row):
        name = str(row['name']).lower()
        if any(x in name for x in ['sữa', 'latte', 'cheese', 'kem', 'yogurt', 'cacao']):
            return 200.0
        return 0.0
        
    def estimate_alcohol(row):
        name = str(row['name']).lower()
        if any(x in name for x in ['bia', 'rượu', 'cocktail', 'wine']):
            return 330.0
        return 0.0

    df['salt'] = df.apply(estimate_salt, axis=1)
    df['milk'] = df.apply(estimate_milk, axis=1)
    df['alcohol'] = df.apply(estimate_alcohol, axis=1)

    # Lưu file
    df.to_csv(OUTPUT_FOOD, index=False)
    print(f"✅ Đã lưu file món ăn sạch tại: {OUTPUT_FOOD}")

def clean_diabetes_data():
    """Xử lý dữ liệu tiểu đường: Encode, lọc nhiễu."""
    print("🔄 Đang xử lý dữ liệu tiểu đường...")
    if not os.path.exists(DIABETES_FILE):
        print(f"❌ Không tìm thấy file: {DIABETES_FILE}")
        return

    df = pd.read_csv(DIABETES_FILE)
    
    # 1. Xóa trùng lặp
    initial_len = len(df)
    df = df.drop_duplicates()
    print(f"   - Đã loại bỏ {initial_len - len(df)} dòng trùng lặp.")
    
    # 2. Encode Gender (Nam=1, Nữ=0)
    # Loại bỏ giới tính 'Other' (số lượng rất ít, thường là nhiễu)
    df = df[df['gender'] != 'Other']
    df['gender'] = df['gender'].map({'Male': 1, 'Female': 0}).astype(int)
    
    # 3. Encode Smoking History (Chuyển sang dạng số để Model hiểu)
    # 0: never, 1: No Info, 2: former/not current, 3: current/ever
    risk_map = {
        'never': 0,
        'No Info': 1,
        'former': 2,
        'not current': 2,
        'current': 3,
        'ever': 3
    }
    df['smoking_history'] = df['smoking_history'].map(risk_map)
    
    # Lưu file
    df.to_csv(OUTPUT_DIABETES, index=False)
    print(f"Đã lưu file tiểu đường sạch tại: {OUTPUT_DIABETES}")

if __name__ == "__main__":
    clean_food_data()
    clean_diabetes_data()

