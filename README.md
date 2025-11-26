# 📘 BÁO CÁO CHI TIẾT QUÁ TRÌNH PHÁT TRIỂN DỰ ÁN: VIETHEALTH AI
**Chủ đề:** Phân tích thói quen sử dụng thực phẩm và dự đoán tiểu đường
**Người thực hiện:** Antigravity (Trợ lý AI) & kwishtt
**Ngày hoàn thành:** 26/11/2025

---

## 🌟 Lời mở đầu
Dự án **VietHealth AI** được xây dựng với sứ mệnh đưa công nghệ Trí tuệ nhân tạo (AI) vào việc chăm sóc sức khỏe đời thường. Không chỉ dừng lại ở lý thuyết, chúng tôi đã xây dựng một hệ thống hoàn chỉnh từ A-Z: bắt đầu từ việc thu thập dữ liệu thô sơ trên mạng, xử lý chúng thành kiến thức, dạy cho máy tính học, và cuối cùng là tạo ra một ứng dụng web đẹp mắt để người dùng dễ dàng tương tác.

Dưới đây là tường thuật chi tiết từng giai đoạn của hành trình này.

---

## 📅 Giai đoạn 1: Khởi tạo & Chuẩn bị (The Foundation)
*Giai đoạn đặt những viên gạch đầu tiên để đảm bảo dự án chạy ổn định.*

### 1. Mục tiêu (Làm gì?)
Tạo ra một môi trường làm việc tiêu chuẩn, đảm bảo rằng khi code được viết ra, nó sẽ chạy mượt mà trên mọi máy tính khác nhau mà không gặp lỗi thiếu công cụ.

### 2. Cách thực hiện (Làm như nào?)
Chúng tôi rà soát lại toàn bộ yêu cầu của dự án và liệt kê ra những "nguyên liệu" cần thiết nhất. Giống như việc trước khi nấu ăn phải chuẩn bị đủ gia vị vậy.

### 3. Công cụ sử dụng (Làm với cái gì?)
*   **Python:** Ngôn ngữ lập trình chính.
*   **File `requirements.txt`:** Một danh sách "đi chợ" chứa tên các thư viện cần cài đặt (như `flask` để làm web, `pandas` để xử lý số liệu...).
*   **File `PROJECT_PLAN.md`:** Bản đồ chỉ đường, vạch rõ các bước cần đi để không bị lạc hướng.

### 4. Đầu ra (Kết quả)
*   ✅ Một cấu trúc thư mục dự án gọn gàng, khoa học.
*   ✅ Môi trường lập trình sẵn sàng hoạt động.

---

## 🛠️ Giai đoạn 2: Kỹ thuật Dữ liệu (Data Engineering)
*Giai đoạn quan trọng nhất - Biến dữ liệu thô thành "vàng".*

### 1. Mục tiêu (Làm gì?)
Máy tính không thể hiểu "Phở bò" hay "Tiểu đường" nếu không có dữ liệu. Mục tiêu là phải tìm cho bằng được dữ liệu về món ăn Việt Nam và hồ sơ bệnh án của người thật.

### 2. Cách thực hiện (Làm như nào?)
Chúng tôi chia làm 2 mũi tấn công:
*   **Mũi 1 (Dữ liệu món ăn):** Viết một con robot phần mềm (gọi là Crawler) truy cập vào trang web `supvn.net`. Robot này sẽ tự động đọc bảng Calories, sao chép thông tin của hàng trăm món ăn và lưu về máy. Sau đó, chúng tôi viết thêm một bộ lọc thông minh để tự động điền các thông tin thiếu (ví dụ: thấy chữ "chiên" thì tự điền thêm chất béo, thấy "bia" thì điền thêm cồn).
*   **Mũi 2 (Dữ liệu bệnh án):** Sử dụng bộ dữ liệu khổng lồ gồm **100,000 hồ sơ bệnh nhân** (có các chỉ số như đường huyết, BMI, tiền sử bệnh...). Chúng tôi làm sạch nó bằng cách xóa các dòng trùng lặp và chuyển đổi chữ viết (Nam/Nữ) thành con số (1/0) để máy tính đọc được.

### 3. Công cụ sử dụng (Làm với cái gì?)
*   **Requests & BeautifulSoup:** Để robot truy cập web và đọc hiểu nội dung HTML.
*   **Pandas:** Công cụ mạnh nhất để xử lý bảng tính (giống như Excel nhưng siêu tốc độ).

### 4. Đầu ra (Kết quả)
*   ✅ File `cac_mon_an.csv`: Chứa danh sách món ăn Việt Nam kèm chỉ số dinh dưỡng (Calo, Đường, Đạm, Béo...).
*   ✅ File `processed_diabetes.csv`: Dữ liệu sạch của 100,000 bệnh nhân, sẵn sàng để dạy cho AI.

---

## 🧠 Giai đoạn 3: Huấn luyện AI (AI Modeling)
*Giai đoạn "thổi hồn" vào cỗ máy - Tạo ra trí thông minh.*

### 1. Mục tiêu (Làm gì?)
Dạy cho máy tính biết cách nhìn vào thói quen ăn uống và chỉ số cơ thể của một người để dự đoán xem họ có nguy cơ mắc bệnh hay không.

### 2. Cách thực hiện (Làm như nào?)
Chúng tôi sử dụng thuật toán **Random Forest (Rừng ngẫu nhiên)**. Hãy tưởng tượng thuật toán này giống như việc tham khảo ý kiến của 100 vị bác sĩ khác nhau cùng lúc.
*   Chúng tôi chia dữ liệu bệnh án làm 2 phần: 80% để dạy máy học, 20% để kiểm tra (thi).
*   Chúng tôi huấn luyện song song **3 mô hình trí tuệ nhân tạo** riêng biệt:
    1.  **Mô hình Tiểu đường:** Chuyên bắt bệnh tiểu đường dựa trên đường huyết và HbA1c.
    2.  **Mô hình Tim mạch:** Chuyên bắt bệnh tim dựa trên tuổi tác và thói quen hút thuốc.
    3.  **Mô hình Huyết áp:** Chuyên dự đoán cao huyết áp.

### 3. Công cụ sử dụng (Làm với cái gì?)
*   **Scikit-learn:** Thư viện chuyên dụng để tạo ra các mô hình học máy (Machine Learning).
*   **Joblib:** Công cụ để "đóng gói" trí tuệ của máy tính lại thành một file để sử dụng sau này.

### 4. Đầu ra (Kết quả)
*   ✅ File `health_model.pkl`: Một file nặng **262 MB**. Đây chính là "bộ não" của hệ thống, chứa đựng toàn bộ tri thức mà máy tính đã học được từ 100,000 bệnh nhân.

---

## 💻 Giai đoạn 4: Phát triển Ứng dụng Web (Web App)
*Giai đoạn "trang điểm" - Đưa công nghệ đến tay người dùng.*

### 1. Mục tiêu (Làm gì?)
Tạo ra một giao diện đẹp, dễ sử dụng để người dùng bình thường (không biết code) cũng có thể nhập thông tin và xem kết quả dự đoán.

### 2. Cách thực hiện (Làm như nào?)
*   **Backend (Phần xử lý ngầm):** Dùng Python (Flask) để kết nối "Bộ não AI" với giao diện web. Khi người dùng nhập món ăn, Backend sẽ tính toán dinh dưỡng, gửi sang AI để khám bệnh, rồi trả kết quả về.
*   **Frontend (Giao diện):**
    *   Thiết kế theo phong cách **Glassmorphism (Kính mờ)**: Tạo cảm giác sang trọng, hiện đại.
    *   Xây dựng tính năng **"Tự động gợi ý" (Autocomplete)**: Người dùng chỉ cần gõ vài chữ, hệ thống sẽ nhắc tên món ăn chuẩn xác.
    *   Vẽ **Biểu đồ Radar (Mạng nhện)**: Hiển thị 3 chỉ số nguy cơ bệnh lý trên cùng một hình vẽ, giúp người dùng nhìn là hiểu ngay tình trạng sức khỏe của mình đang lệch về hướng nào.

### 3. Công cụ sử dụng (Làm với cái gì?)
*   **Flask:** Khung phần mềm để chạy web server.
*   **HTML/CSS/JS:** Để xây dựng giao diện và hiệu ứng động.
*   **Chart.js:** Để vẽ biểu đồ đẹp mắt.

### 4. Đầu ra (Kết quả)
*   ✅ Một trang web hoàn chỉnh chạy tại địa chỉ `http://127.0.0.1:5000`.
*   ✅ Người dùng có thể nhập tuổi, chiều cao, cân nặng và thực đơn ăn uống.
*   ✅ Hệ thống trả về ngay lập tức: Tổng lượng Calo/Đường nạp vào, Chỉ số BMI, và Nguy cơ mắc 3 loại bệnh (Tiểu đường, Tim mạch, Huyết áp).

---

## 🏁 Tổng kết
Dự án này là một ví dụ điển hình cho quy trình làm việc chuyên nghiệp: Từ việc đi tìm nguyên liệu thô (Dữ liệu), chế biến tinh xảo (AI), cho đến việc bày biện đẹp mắt (Web App). Kết quả là một sản phẩm công nghệ có giá trị thực tiễn cao, giúp mọi người chủ động bảo vệ sức khỏe của chính mình.
