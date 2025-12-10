# 🚀 ĐỀ XUẤT ĐỀ TÀI BTL: Trợ lý AI Tra cứu Pháp luật/Quy chế (RAG Chatbot)

Chào anh em, sau khi nghiên cứu kỹ các hướng đi cho bài tập lớn lần này, mình đề xuất team chọn đề tài: **Xây dựng Hệ thống Chatbot RAG (Retrieval-Augmented Generation) cho Tiếng Việt.**

Dưới đây là 4 lý do cốt lõi tại sao đây là lựa chọn "Ngon - Bổ - Rẻ" nhất cho team mình lúc này:

## 1. Giải quyết vấn đề "Ảo giác" của ChatGPT (Điểm cộng về tính ứng dụng)
* [cite_start]**Vấn đề:** Các mô hình như ChatGPT thường chém gió lung tung (hallucination) và không biết về các tài liệu nội bộ (ví dụ: Quy chế trường mình, hay các luật mới nhất)[cite: 97, 98].
* **Giải pháp của chúng ta:** Sử dụng kỹ thuật **RAG**. Hệ thống sẽ tìm kiếm thông tin trong kho dữ liệu PDF mà ta cung cấp, sau đó mới trả lời.
* **Điểm "Wow" khi bảo vệ:** Chatbot của ta có khả năng **Trích dẫn nguồn** (Citation). Ví dụ: *"Thông tin này nằm ở Điều 5, Khoản 2..."*. [cite_start]Đây là tính năng "sát thủ" để chứng minh độ tin cậy[cite: 128].

## 2. Công nghệ "Hot Trend" 2024-2025 nhưng KHÔNG cần GPU khủng
* [cite_start]Khác với Computer Vision (như đề tài nhận diện mũ bảo hiểm PPE) cần GPU mạnh để train/fine-tune rất cực khổ[cite: 11, 42], đề tài RAG tập trung vào kiến trúc hệ thống.
* [cite_start]Chúng ta có thể chạy **local** trên máy cá nhân hoặc **Google Colab** nhẹ nhàng vì chủ yếu gọi API[cite: 117].
* [cite_start]Đây là cơ hội để anh em tiếp cận các từ khóa tuyển dụng hot nhất hiện nay: **Vector Database (ChromaDB), LangChain, Embedding, Prompt Engineering**[cite: 101, 112].

## 3. Chi phí bằng 0 - Tốc độ cực nhanh
* [cite_start]Thay vì tốn tiền mua API OpenAI, ta sẽ dùng **Gemini API** (đang miễn phí gói Flash/Pro) hoặc **Groq API** chạy Llama 3[cite: 123, 124].
* [cite_start]Groq giúp demo chạy "nhanh như điện", tạo ấn tượng cực mạnh về độ mượt mà khi thuyết trình[cite: 124].

## 4. Phân chia công việc rõ ràng, dễ làm việc nhóm
Đề tài này rất dễ tách module để anh em cùng làm song song mà không dẫm chân nhau:
* [cite_start]**Bạn A (Data Engineer):** Thu thập PDF luật/quy chế, dùng LangChain để cắt nhỏ văn bản (Chunking) và xử lý vấn đề từ ghép tiếng Việt[cite: 115].
* [cite_start]**Bạn B (Backend/AI):** Dựng Vector Database, viết hàm tìm kiếm (Retriever) và chọn model Embedding tiếng Việt xịn (như `bkai-foundation-models`)[cite: 108, 116].
* **Bạn C (Frontend):** Dùng **Streamlit** hoặc Chainlit dựng giao diện chat. [cite_start]Streamlit hỗ trợ session state rất tốt để lưu lịch sử chat[cite: 157].

---
### 💡 Kết luận
Chọn đề tài này là chọn sự **An toàn nhưng Ấn tượng**. Chúng ta không lo bị fail do model không hội tụ (như train AI truyền thống), mà vẫn có sản phẩm mang tính công nghệ cao để demo.

Mọi người xem qua và chốt sớm để triển khai nhé!
