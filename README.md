# ĐỀ XUẤT ĐỀ TÀI BÀI TẬP LỚN: TRỢ LÝ AI TRA CỨU PHÁP LUẬT & QUY CHẾ (RAG SYSTEM)

## 1. Tên Đề tài
**Xây dựng Hệ thống Chatbot Tra cứu Văn bản Pháp luật và Quy chế Đào tạo sử dụng Kỹ thuật RAG (Retrieval-Augmented Generation)**

## 2. Đặt vấn đề và Tính cấp thiết
Hiện nay, việc tra cứu thông tin trong các văn bản quy phạm pháp luật hoặc quy chế nội bộ (Sổ tay sinh viên, Quy chế đào tạo) gặp nhiều khó khăn:
* **Công cụ tìm kiếm từ khóa (Keyword Search)** truyền thống thường trả về quá nhiều kết quả không liên quan hoặc đòi hỏi người dùng phải biết chính xác từ khóa chuyên ngành.
* **Các mô hình ngôn ngữ lớn (LLM)** như ChatGPT có khả năng trả lời tự nhiên nhưng thường xuyên gặp lỗi "ảo giác" (hallucination) - tự bịa đặt thông tin sai lệch, hoặc thiếu kiến thức về các dữ liệu nội bộ/dữ liệu mới cập nhật.

**Giải pháp:** Ứng dụng kỹ thuật **RAG (Retrieval-Augmented Generation)** để kết hợp khả năng tìm kiếm chính xác của máy tính với khả năng diễn đạt ngôn ngữ tự nhiên của AI, đảm bảo câu trả lời luôn có căn cứ và trích dẫn nguồn rõ ràng.

## 3. Mục tiêu Đề tài
* Xây dựng được pipeline xử lý dữ liệu văn bản Tiếng Việt (PDF/Docx) tự động.
* Tạo ra hệ thống Chatbot có khả năng trả lời câu hỏi dựa trên ngữ cảnh tài liệu cung cấp.
* **Tính năng cốt lõi:** Câu trả lời phải đi kèm **Trích dẫn nguồn (Citation)** (Ví dụ: *Thông tin này được quy định tại Điều 5, Khoản 2 của Văn bản X*).

## 4. Phương pháp và Công nghệ Triển khai

### 4.1. Kiến trúc Hệ thống
Sử dụng kiến trúc RAG tiêu chuẩn với Framework **LangChain**:
1.  **Document Loading:** Tải và chuẩn hóa văn bản từ các file PDF/Word.
2.  **Splitting & Chunking:** Kỹ thuật chia nhỏ văn bản thông minh (Recursive Character Splitter) để đảm bảo ngữ cảnh không bị cắt rời, tối ưu cho Tiếng Việt.
3.  **Embedding:** Mã hóa văn bản thành vector.
4.  **Vector Store:** Lưu trữ và truy xuất vector.
5.  **LLM Generation:** Sinh câu trả lời từ ngữ cảnh tìm được.

### 4.2. Tech Stack Dự kiến
* **Ngôn ngữ:** Python.
* **Framework:** LangChain (Quản lý luồng xử lý), Streamlit (Giao diện Web Demo).
* **Mô hình Embedding (Quan trọng):** Sử dụng các mô hình tối ưu cho Tiếng Việt như `BKAI-Foundation-models/vietnamese-bi-encoder` hoặc `PhoBERT` để đảm bảo độ chính xác khi tìm kiếm ngữ nghĩa.
* **Vector Database:** ChromaDB hoặc FAISS (Open-source, chạy local, không tốn chi phí).
* **Large Language Model (LLM):** * *Phương án 1:* Gemini API (Google) - Miễn phí, cửa sổ ngữ cảnh lớn.
    * *Phương án 2:* Llama 3 qua Groq API - Tốc độ phản hồi cực nhanh (Real-time).

## 5. Kế hoạch Thực hiện và Kết quả Dự kiến
* **Giai đoạn 1 (Tuần 1-2):** Thu thập dữ liệu (Sổ tay sinh viên, Luật Giáo dục, Luật Lao động...) và làm sạch dữ liệu. Xây dựng module Vector Database.
* **Giai đoạn 2 (Tuần 3-4):** Tích hợp LangChain và LLM. Tinh chỉnh (Fine-tune) câu lệnh Prompt (Prompt Engineering) để chatbot không trả lời sai sự thật.
* **Giai đoạn 3 (Tuần 5):** Xây dựng giao diện Streamlit. Hiển thị song song khung chat và khung xem tài liệu gốc.

## 6. Giá trị Đóng góp của Đề tài
* **Về mặt học thuật:** Minh chứng khả năng áp dụng các kỹ thuật NLP tiên tiến (Embeddings, Vector Search) cho ngôn ngữ tiếng Việt, giải quyết bài toán đặc thù về từ ghép và ngữ nghĩa.
* **Về mặt thực tiễn:** Sản phẩm có thể ứng dụng ngay vào việc hỗ trợ giải đáp thắc mắc tự động cho Phòng Đào tạo hoặc bộ phận Hành chính Nhân sự.
