# Board Game Database Project (HUST - Database Lab)

Dự án xây dựng cơ sở dữ liệu quan hệ trên PostgreSQL để quản lý hệ sinh thái BoardGameGeek. Hệ thống được thiết kế chuẩn 3NF và xử lý tập dữ liệu khổng lồ với gần 19 triệu lượt đánh giá bằng luồng ETL tự động.

---

## 1. Yêu cầu hệ thống
- **Python 3.x** và thư viện Pandas (cài đặt: pip install pandas)
- **PostgreSQL** và phần mềm quản trị **pgAdmin 4**
- Git (để tải mã nguồn cập nhật nhất)

---

## 2. Lấy dữ liệu gốc (VUI LÒNG ĐỌC KỸ)
Vì dữ liệu thô nặng hàng GB, các file này đã được bỏ qua bằng `.gitignore` để không làm nặng kho chứa chung. Mọi người tải code về (clone) xong cần tự setup dữ liệu theo đúng các bước sau:

1. Truy cập Kaggle: [Board Games Database from BoardGameGeek](https://www.kaggle.com/datasets/threnjen/board-games-database-from-boardgamegeek?select=user_ratings.csv)
2. **⚠️ LƯU Ý QUAN TRỌNG:** Để tiết kiệm dung lượng, **KHÔNG** tải toàn bộ (Download All). Hãy tải thủ công đúng 4 file CSV sau:
   - games.csv
   - mechanics.csv
   - themes.csv
   - user_ratings.csv
3. Tại thư mục gốc của project (nơi chứa file preprocessing.py), tạo một thư mục mới tên là **origin_data**.
4. Chép 4 file CSV vừa tải ở trên vào thư mục origin_data này.

---

## 3. Tiền xử lý dữ liệu (ETL)
Mở Terminal ngay tại thư mục dự án trên VS Code và chạy lệnh:

python preprocessing.py

*Lưu ý:* File Python này đã được cấu hình dùng **đường dẫn tương đối (./)**, nên mọi người chạy trên máy nào cũng sẽ tự động hoạt động. Kịch bản sẽ tự động dọn dẹp, xử lý lỗi ép kiểu, xóa dòng trùng và xuất các file sạch vào một thư mục mới tên là **new_data**.

---

## 4. Khởi tạo Database và Xây dựng cấu trúc
1. Mở pgAdmin 4, tạo một CSDL mới (ví dụ: boardgamedb).
2. Mở **Query Tool**, copy toàn bộ code trong file **01_schema.sql** và chạy (Execute). Bước này sẽ tạo ra 7 bảng chuẩn 3NF và thiết lập các khóa chính/khóa ngoại.

---

## 5. Nạp dữ liệu vào Database (BƯỚC QUAN TRỌNG NHẤT)
Lệnh COPY của PostgreSQL giao tiếp trực tiếp với hệ điều hành máy chủ nên **BẮT BUỘC PHẢI DÙNG ĐƯỜNG DẪN TUYỆT ĐỐI (Absolute Path)**, không thể dùng ./ như Python. 

Mọi người làm theo đúng 3 thao tác sau:

1. Mở file **02_import_data.sql** trên VS Code.
2. Bấm Ctrl + H (Find and Replace). 
   - Tại ô **Find**, nhập: [ĐƯỜNG_DẪN_TỚI_THƯ_MỤC_PROJECT_CỦA_BẠN]
   - Tại ô **Replace**, nhập **đường dẫn thực tế đến thư mục project trên máy tính của bạn**. (Ví dụ: D:/HocTap/boardgame-db). Đảm bảo giữ lại dấu / ở cuối nối với thư mục new_data.
   - Bấm **Replace All**.
3. Copy toàn bộ các lệnh sau khi đã đổi đường dẫn, dán vào Query Tool trên pgAdmin và bấm Play (Execute).

**⏳ CHÚ Ý THỜI GIAN CHẠY:**
File nạp dữ liệu sẽ chạy qua 7 bảng. Riêng bảng reviews chứa gần 19 triệu bản ghi, hệ thống sẽ mất khoảng **2 đến 5 phút** để kiểm tra khóa chính và nạp vào ổ cứng. **Tuyệt đối không tắt pgAdmin hay bấm Cancel giữa chừng để tránh lỗi treo Database.**
