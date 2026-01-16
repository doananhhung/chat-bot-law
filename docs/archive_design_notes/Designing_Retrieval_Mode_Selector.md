# Designing: Retrieval Mode Selector

## 1. Tổng quan

### Mục tiêu
Cho phép người dùng chọn chế độ tìm kiếm (retrieval) thông qua giao diện Streamlit để cân bằng giữa **tốc độ** và **độ chính xác**.

### Dữ liệu Benchmark hiện có
Từ file `benchmark_results.json`:
- Index type: **IVF** (1,530 vectors, 768D)
- nlist: 64 clusters
- Latency với nprobe=8: ~87ms (avg), 85ms (p50), 108ms (p95)

### 3 Chế độ đề xuất

| Chế độ | nprobe | Recall ước tính | Latency | Use case |
|--------|--------|-----------------|---------|----------|
| **Chính xác cao** | 64 (=nlist) | ~100% | Chậm nhất | Cần kết quả chính xác tuyệt đối |
| **Cân bằng** | 8 | ~96% | Trung bình | Sử dụng hàng ngày (mặc định) |
| **Tốc độ cao** | 2 | ~80-85% | Nhanh nhất | Query nhanh, chấp nhận miss một số kết quả |

---

## 2. Phân tích kỹ thuật

### 2.1 Hiện trạng

**Retriever** (`src/rag_engine/retriever.py`):
- `SemanticRetriever` load FAISS index và set nprobe từ `AppConfig.IVF_NPROBE`
- Có sẵn method `_get_ivf_index()` để truy cập IVF index
- Có sẵn method `get_index_info()` trả về thông tin index

**App** (`app.py`):
- Retriever được cache qua `@st.cache_resource` → chỉ load 1 lần
- Cần cách thay đổi nprobe runtime mà không reload

**Config** (`src/config.py`):
- `IVF_NPROBE = 8` (mặc định)
- `IVF_NLIST = 64`

### 2.2 Giới hạn
- Chỉ áp dụng cho **IVF index** (không áp dụng cho Flat index)
- Nếu dùng Flat index, UI sẽ disable tùy chọn và hiển thị thông báo

---

## 3. Thiết kế chi tiết

### 3.1 Thay đổi trong `src/rag_engine/retriever.py`

Thêm 2 method mới vào class `SemanticRetriever`:

```python
def set_search_mode(self, mode: str) -> bool:
    """
    Set search mode cho IVF index.

    Args:
        mode: "quality" | "balanced" | "speed"

    Returns:
        True nếu set thành công, False nếu không phải IVF index
    """
    # Lấy IVF index
    # Map mode -> nprobe value
    # Set nprobe
    # Return success/failure

def get_current_search_mode(self) -> dict:
    """
    Trả về thông tin search mode hiện tại.

    Returns:
        {
            "mode": "quality" | "balanced" | "speed",
            "nprobe": int,
            "nlist": int,
            "is_ivf": bool,
            "search_scope_pct": float  # % clusters được search
        }
    """
```

**Mode mapping:**
```python
MODE_CONFIG = {
    "quality": nlist,        # 64 → search tất cả clusters
    "balanced": 8,           # ~12.5% clusters
    "speed": 2,              # ~3% clusters
}
```

### 3.2 Thay đổi trong `app.py`

**Vị trí UI:** Trong sidebar, dưới phần "Quản lý Dữ liệu"

**UI Components:**
```python
with st.expander("⚡ Chế độ tìm kiếm"):
    # Radio button cho 3 chế độ
    search_mode = st.radio(
        "Chọn chế độ:",
        options=["balanced", "quality", "speed"],
        format_func=lambda x: {
            "quality": "🎯 Chính xác cao",
            "balanced": "⚖️ Cân bằng (Khuyến nghị)",
            "speed": "🚀 Tốc độ cao"
        }[x],
        index=0,  # balanced là mặc định
        help="Điều chỉnh cân bằng giữa tốc độ và độ chính xác"
    )

    # Hiển thị thông tin mode hiện tại
    mode_info = retriever.get_current_search_mode()
    st.caption(f"Phạm vi tìm kiếm: {mode_info['search_scope_pct']}% clusters")
```

**Logic flow:**
1. Khi user thay đổi radio → lưu vào `st.session_state.search_mode`
2. Trước mỗi query, gọi `retriever.set_search_mode(st.session_state.search_mode)`
3. Hiển thị badge/indicator trong chat area cho biết mode đang dùng

### 3.3 Session State

```python
# Khởi tạo
if "search_mode" not in st.session_state:
    st.session_state.search_mode = "balanced"
```

### 3.4 Xử lý Flat Index

Nếu index không phải IVF:
- Disable radio buttons
- Hiển thị: "Index hiện tại là Flat (tìm kiếm chính xác), không cần điều chỉnh"

---

## 4. Files cần thay đổi

| File | Thay đổi |
|------|----------|
| `src/rag_engine/retriever.py` | Thêm `set_search_mode()` và `get_current_search_mode()` |
| `app.py` | Thêm UI expander trong sidebar, logic apply mode |

---

## 5. Kế hoạch thực hiện

### Bước 1: Update Retriever
- [ ] Thêm `set_search_mode(mode: str) -> bool`
- [ ] Thêm `get_current_search_mode() -> dict`
- [ ] Test methods hoạt động đúng

### Bước 2: Update App UI
- [ ] Thêm session state cho search_mode
- [ ] Thêm UI expander với radio buttons
- [ ] Hiển thị thông tin mode hiện tại

### Bước 3: Kết nối Logic
- [ ] Gọi `set_search_mode()` trước khi query
- [ ] Xử lý case Flat index (disable UI)

### Bước 4: Testing
- [ ] Test chuyển đổi giữa các mode
- [ ] Test với Flat index
- [ ] Test với IVF index
- [ ] Verify latency thay đổi theo mode

---

## 6. UI Mockup

```
┌─────────────────────────────────┐
│ 🗂️ Quản lý Hội thoại            │
│ ➕ Cuộc hội thoại mới           │
│─────────────────────────────────│
│ Gần đây                         │
│ 💬 Session 1                    │
│ 💬 Session 2                    │
│─────────────────────────────────│
│ ⚙️ Quản lý Dữ liệu        [▼]   │
│─────────────────────────────────│
│ ⚡ Chế độ tìm kiếm        [▼]   │  ← NEW
│ ┌─────────────────────────────┐ │
│ │ ○ 🎯 Chính xác cao          │ │
│ │ ● ⚖️ Cân bằng (Khuyến nghị) │ │
│ │ ○ 🚀 Tốc độ cao             │ │
│ │                             │ │
│ │ 📊 Phạm vi: 12.5% clusters  │ │
│ │ ⏱️ Latency: ~87ms           │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

## 7. Verification (Kiểm tra sau khi hoàn thành)

1. **Chạy app:** `streamlit run app.py`
2. **Kiểm tra UI:** Mở sidebar → thấy expander "Chế độ tìm kiếm"
3. **Test chuyển mode:** Chọn từng mode, verify thông tin hiển thị thay đổi
4. **Test query:** Gửi câu hỏi, kiểm tra log xem nprobe có đúng không
5. **Test Flat index:** Nếu có thể, test với Flat index để verify UI disable đúng cách
