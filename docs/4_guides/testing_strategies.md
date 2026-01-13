# Chiến lược Testing

Để đảm bảo hệ thống hoạt động chính xác (đặc biệt là tính đúng đắn của câu trả lời pháp lý), chúng ta áp dụng các tầng test sau.

## 1. Unit Tests (Kiểm thử đơn vị)
Nằm trong thư mục `tests/`.
*   **Mục tiêu**: Test từng hàm riêng lẻ (hàm load file, hàm split text, hàm query database).
*   **Công cụ**: `pytest`.
*   **Cách chạy**:
    ```bash
    pytest tests/test_ingestion.py
    ```

## 2. Integration Tests (Kiểm thử tích hợp)
*   **Mục tiêu**: Test sự phối hợp giữa các module (ví dụ: Ingestion -> Vector DB -> Retrieval).
*   **Ví dụ**: Test xem file PDF nạp vào có tìm lại được đúng đoạn text đó không.

## 3. RAG Evaluation (Đánh giá chất lượng RAG) - **Quan trọng**
Khác với phần mềm thông thường, Chatbot cần đánh giá "chất lượng câu trả lời".
Chúng ta sử dụng bộ framework (ví dụ RAGAS hoặc tự viết script benchmark) để đo:
*   **Context Precision**: Dữ liệu tìm được có liên quan câu hỏi không?
*   **Faithfulness**: Câu trả lời có bịa đặt (hallucination) không? Có dựa trên context không?

### Script Benchmark hiện có
Trong thư mục `tests/`, có file `benchmark_retrieval.py`.
Script này sẽ:
1.  Đọc một bộ câu hỏi mẫu (Ground Truth).
2.  Chạy qua hệ thống Retrieval.
3.  So sánh xem tài liệu trả về có chứa đáp án đúng không.

```bash
python tests/benchmark_retrieval.py
```

## Quy tắc đóng góp (Contribution Rule)
*   Trước khi push code, hãy chạy `pytest`.
*   Nếu sửa logic RAG, hãy chạy benchmark để đảm bảo độ chính xác không bị giảm.
