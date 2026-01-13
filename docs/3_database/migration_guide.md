# Hướng dẫn Migration Database

Hiện tại dự án đang ở giai đoạn MVP và chưa tích hợp Alembic. Việc thay đổi cấu trúc bảng (Schema) cần được thực hiện cẩn thận để tránh mất dữ liệu.

## Quy trình thay đổi Schema (Hiện tại)

Nếu bạn sửa file `src/database/models.py` (ví dụ thêm cột `user_id`):

### Cách 1: Reset toàn bộ (Dữ liệu test)
Đây là cách nhanh nhất nếu bạn không quan trọng dữ liệu cũ.
1.  Dừng chương trình.
2.  Xóa file `data/chat_history.db`.
3.  Chạy lại chương trình (`streamlit run app.py`).
4.  Hệ thống sẽ tự tạo lại file DB với cấu trúc mới.

### Cách 2: Cập nhật thủ công (Giữ dữ liệu)
1.  Tải và cài đặt **DB Browser for SQLite**.
2.  Mở file `data/chat_history.db`.
3.  Chuyển sang tab **Execute SQL**.
4.  Chạy lệnh SQL tương ứng với thay đổi của bạn. Ví dụ thêm cột:
    ```sql
    ALTER TABLE chat_sessions ADD COLUMN user_id TEXT;
    ```
5.  Lưu thay đổi (Write Changes).

## Kế hoạch tương lai (Alembic)
Khi dự án đi vào ổn định (Production), chúng ta sẽ setup Alembic:
1.  `pip install alembic`
2.  `alembic init alembic`
3.  Cấu hình `alembic.ini` và `env.py` trỏ về `Base` model.
4.  Quy trình sẽ là:
    *   Sửa code model.
    *   `alembic revision --autogenerate -m "Added user_id"`
    *   `alembic upgrade head`
