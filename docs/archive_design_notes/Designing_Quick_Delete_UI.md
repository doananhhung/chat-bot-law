# TÀI LIỆU THIẾT KẾ: GIAO DIỆN XÓA NHANH (SIDEBAR)
**Ngày:** 2026-01-13
**Trạng thái:** DRAFT
**Bối cảnh:** Quy trình xóa hiện tại yêu cầu người dùng chọn một cuộc hội thoại, mở expander cài đặt, và click nút xóa. Điều này quá nhiều click để quản lý nhiều chat.

---

## 1. MỤC TIÊU
Cải thiện Trải nghiệm Người dùng (UX) bằng cách đặt nút "Xóa Nhanh" (ví dụ: `x` hoặc `🗑️`) trực tiếp bên cạnh mỗi tiêu đề hội thoại trong danh sách lịch sử Sidebar.

## 2. TRẠNG THÁI HIỆN TẠI
*   **Cấu trúc**: Sidebar lặp qua `recent_sessions` và render một `st.button` đơn (full width) cho mỗi session.
*   **Code Snippet**:
    ```python
    for s in recent_sessions:
        if st.button(label, ...): switch_session()
    ```

## 3. LAYOUT UI ĐỀ XUẤT

Để đạt được layout "Tiêu đề + Nút Xóa" trong Streamlit, chúng ta sẽ sử dụng `st.columns` cho mỗi item trong danh sách.

### Mockup Layout
```text
| Sidebar ------------------------|
|                                 |
| [ + Chat Mới ]                  |
|                                 |
| Gần đây:                        |
| [Chat A               ] [ X ]   |
| [Chat B (Active)      ] [ X ]   |
| [Chat C               ] [ X ]   |
|                                 |
|---------------------------------|
```

### Chiến lược Component Kỹ thuật
*   **Grid System**: Sử dụng `col1, col2 = st.columns([0.85, 0.15])`.
*   **Column 1 (Chọn)**: Chứa nút tiêu đề session. Click vào sẽ chuyển đổi `session_id`.
*   **Column 2 (Xóa)**: Chứa nút xóa (icon `✖` hoặc `🗑`). Click vào sẽ kích hoạt logic xóa.

## 4. LOGIC TƯƠNG TÁC

### 4.1. Chọn một Session (Column 1)
*   **Hành động**: Người dùng click vào Tiêu đề.
*   **Kết quả**:
    *   Cập nhật `st.session_state.session_id`.
    *   `st.rerun()`.

### 4.2. Xóa một Session (Column 2)
*   **Hành động**: Người dùng click `✖`.
*   **Logic**:
    1.  **Backend**: Gọi `repo.delete_session(target_id)`.
    2.  **Kiểm tra State**:
        *   **Kịch bản A: Người dùng xóa session KHÔNG ACTIVE.**
            *   Không thay đổi `st.session_state.session_id`.
            *   Chỉ `st.rerun()` để refresh danh sách.
        *   **Kịch bản B: Người dùng xóa session ĐANG ACTIVE.**
            *   View hiện tại không còn hợp lệ.
            *   Logic: Chuyển sang session *có sẵn tiếp theo* trong danh sách.
            *   Nếu danh sách trống (người dùng xóa cái cuối cùng), tự động tạo session "New Chat" mới.
            *   Cập nhật `st.session_state.session_id`.
            *   `st.rerun()`.

## 5. KẾ HOẠCH TRIỂN KHAI CHI TIẾT

### Bước 1: CSS Tweaks (Tùy chọn nhưng Khuyến nghị)
Các columns trong Streamlit đôi khi có khoảng cách lớn. Chúng ta có thể cần CSS tùy chỉnh nhỏ để giảm padding giữa nút Tiêu đề và nút Xóa cho giao diện liền mạch.

### Bước 2: Refactor Sidebar Loop
Sửa đổi vòng lặp `for s in recent_sessions:` trong `app.py`.

**Pseudocode:**
```python
for s in recent_sessions:
    col_nav, col_del = st.columns([0.85, 0.15])

    with col_nav:
        # Highlight active
        type_ = "primary" if s.id == st.session_state.session_id else "secondary"
        if st.button(s.title, key=f"nav_{s.id}", type=type_):
            switch_session(s.id)

    with col_del:
        # Sử dụng key riêng biệt
        if st.button("🗑", key=f"del_{s.id}", help="Xóa hội thoại này"):
            handle_specific_delete(s.id)
```

### Bước 3: Cập nhật Helper Functions
Refactor `handle_delete_session` để nhận một `target_id` rõ ràng (cái cần xóa) và so sánh với `current_id` (cái đang xem) để quyết định có cần chuyển đổi hay không.

## 6. EDGE CASES & RỦI RO

*   **Xóa Nhầm**: Vì `st.button` thực thi ngay lập tức, không có xác nhận "Bạn có chắc chắn?".
    *   *Giảm thiểu*: Trong giai đoạn MVP này, chúng ta chấp nhận rủi ro này để đổi lấy tốc độ (theo yêu cầu "Xóa Nhanh"). Trong tương lai, chúng ta có thể sử dụng `st.popover` (nếu nâng cấp Streamlit) hoặc toast "Hoàn tác".
*   **Tiêu đề Dài**: Tiêu đề dài có thể bị cắt xấu trong column 85% width. Streamlit xử lý bằng cách ellipsizing, có thể chấp nhận được.
*   **Giao diện Mobile**: Trên màn hình rất hẹp, tỷ lệ [0.85, 0.15] có thể làm nút xóa bị bẹp. Streamlit xếp chồng columns trên mobile, có thể trông như "Tiêu đề" rồi "Xóa" bên dưới.
    *   *Giảm thiểu*: Kiểm tra hành vi `st.columns`. Thông thường, nó giữ side-by-side trên chiều rộng hợp lý, nhưng xếp chồng trên mobile. Điều này có thể chấp nhận cho hiện tại.
