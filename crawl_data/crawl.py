import requests
import os

CSV_URL = "https://file.hstatic.net/200000445557/file/nutritionfood_ec2ac1b6d085475e80a7dd31c1595190.csv"
OUTPUT_FILE = "cac_mon_an_crawled.csv"

def download_csv():
    print(f"🔄 Đang tải dữ liệu từ {CSV_URL}...")
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        
        # Lưu file với encoding utf-8-sig để mở trên Excel không lỗi font
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
            
        print(f"🎉 Đã tải thành công và lưu tại {OUTPUT_FILE}")
        
        # Đếm số dòng
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"📊 Tổng số dòng dữ liệu: {len(lines)}")
            
    except Exception as e:
        print(f"❌ Lỗi khi tải file: {e}")

if __name__ == "__main__":
    download_csv()
