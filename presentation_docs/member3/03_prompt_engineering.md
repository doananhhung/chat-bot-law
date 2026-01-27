# 📝 Prompt Engineering - Kỹ Thuật Thiết Kế Prompt

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- Prompt Engineering là gì
- Các kỹ thuật prompt trong dự án
- IRAC structure cho legal domain
- Chain-of-Thought reasoning

---

## 1. Prompt Engineering là gì?

### 1.1 Định nghĩa
**Prompt Engineering** là nghệ thuật và khoa học thiết kế input cho LLM để nhận được output chất lượng cao.

### 1.2 Tại sao quan trọng?

```
Same LLM, Different Prompts:

Prompt 1: "Nói về thai sản"
→ "Thai sản là quá trình mang thai và sinh con..."
   ❌ Generic, no legal focus

Prompt 2: "Bạn là Cố vấn Pháp lý AI cấp cao. Dựa trên tài liệu sau..."
→ "Theo Điều 139 Bộ luật Lao động, lao động nữ được nghỉ..."
   ✅ Professional, cited, structured
```

---

## 2. Prompt Components

### 2.1 System Prompt vs User Prompt

```
┌─────────────────────────────────────────────────────────────┐
│                     SYSTEM PROMPT                            │
│    (Định nghĩa persona, instruction, constraints)           │
│    "Bạn là Cố vấn Pháp lý AI cấp cao..."                   │
├─────────────────────────────────────────────────────────────┤
│                      USER PROMPT                             │
│    (Context + Question + Output format)                     │
│    "[TÀI LIỆU THAM KHẢO]..."                               │
│    "[CÂU HỎI]..."                                          │
│    "[YÊU CẦU TRẢ LỜI]..."                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. QA Prompt trong dự án

### 3.1 System Prompt

```python
# src/rag_engine/prompts.py

QA_SYSTEM_PROMPT = """Bạn là Cố vấn Pháp lý AI cấp cao, 
chuyên sâu về Luật Lao động Việt Nam.
Phong cách trả lời: Chuyên nghiệp, Khách quan, Dựa trên bằng chứng, Logic chặt chẽ.

NHIỆM VỤ CỦA BẠN:
Phân tích câu hỏi và Context (Tài liệu tham khảo) được cung cấp 
để đưa ra tư vấn pháp lý chính xác nhất.

QUY TRÌNH TƯ DUY (Chain of Thought):
1. Đọc kỹ câu hỏi để xác định vấn đề pháp lý cốt lõi.
2. Rà soát phần [TÀI LIỆU THAM KHẢO] để tìm các Điều khoản, Quy định liên quan.
3. Tổng hợp thông tin từ nhiều đoạn văn bản (nếu có) để có cái nhìn toàn diện.
4. Xây dựng câu trả lời theo cấu trúc IRAC (Vấn đề - Căn cứ - Phân tích - Kết luận).

NGUYÊN TẮC BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (Hallucination). 
   Nếu Context không có thông tin, trả lời: "Dựa trên tài liệu hiện có, 
   tôi chưa tìm thấy thông tin cụ thể về vấn đề này."
2. CHỈ sử dụng thông tin từ Context được cung cấp.
3. LUÔN trích dẫn nguồn cụ thể ngay sau thông tin được sử dụng 
   (Ví dụ: [Nguồn: file_abc.pdf, Trang: 10]).
4. Trả lời bằng tiếng Việt, trình bày chuyên nghiệp bằng Markdown."""
```

### 3.2 User Prompt Template

```python
QA_USER_PROMPT_TEMPLATE_STR = """[TÀI LIỆU THAM KHẢO]
{context}

[CÂU HỎI CỦA NGƯỜI DÙNG]
{question}

[YÊU CẦU TRẢ LỜI]
Hãy đóng vai Cố vấn Pháp lý và trả lời câu hỏi trên theo cấu trúc sau:
### 1. Căn cứ pháp lý
(Liệt kê các văn bản, điều luật, trang cụ thể từ tài liệu tham khảo)

### 2. Nội dung tư vấn & Phân tích
(Phân tích chi tiết sự tương quan giữa quy định pháp luật và trường hợp của người dùng)

### 3. Kết luận
(Tóm tắt câu trả lời trực tiếp và đưa ra lời khuyên ngắn gọn)"""
```

---

## 4. IRAC Structure

### 4.1 IRAC là gì?

| Component | Meaning | Purpose |
|-----------|---------|---------|
| **I**ssue | Vấn đề | Xác định câu hỏi pháp lý |
| **R**ule | Căn cứ | Điều luật, quy định áp dụng |
| **A**nalysis | Phân tích | Áp dụng rule vào case |
| **C**onclusion | Kết luận | Trả lời trực tiếp |

### 4.2 IRAC trong response

```markdown
### 1. Căn cứ pháp lý
- Điều 139 Bộ luật Lao động 2019 [Nguồn: blld.pdf, Trang: 46]
- Nghị định 145/2020/NĐ-CP [Nguồn: nd145.pdf, Trang: 12]

### 2. Nội dung tư vấn & Phân tích
Theo Điều 139, lao động nữ được nghỉ thai sản trước và sau 
khi sinh con tổng cộng là 6 tháng...

### 3. Kết luận
Bạn được nghỉ thai sản 6 tháng. Nếu sinh đôi, được cộng thêm 
1 tháng cho mỗi con từ con thứ 2.
```

---

## 5. Chain-of-Thought (CoT)

### 5.1 Ý tưởng

Hướng dẫn LLM "suy nghĩ từng bước" thay vì trả lời trực tiếp.

### 5.2 Trong System Prompt

```python
QUY TRÌNH TƯ DUY (Chain of Thought):
1. Đọc kỹ câu hỏi để xác định vấn đề pháp lý cốt lõi.
2. Rà soát phần [TÀI LIỆU THAM KHẢO] để tìm các Điều khoản liên quan.
3. Tổng hợp thông tin từ nhiều đoạn văn bản (nếu có).
4. Xây dựng câu trả lời theo cấu trúc IRAC.
```

### 5.3 Tại sao CoT hiệu quả?

| Without CoT | With CoT |
|-------------|----------|
| Jump to conclusion | Step-by-step reasoning |
| May miss context | Uses all context |
| Lower accuracy | Higher accuracy |

---

## 6. Anti-Hallucination Techniques

### 6.1 Explicit Constraints

```python
NGUYÊN TẮC BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (Hallucination).
   Nếu Context không có thông tin, trả lời: 
   "Dựa trên tài liệu hiện có, tôi chưa tìm thấy..."
2. CHỉ sử dụng thông tin từ Context được cung cấp.
```

### 6.2 Mandatory Citations

```python
3. LUÔN trích dẫn nguồn cụ thể ngay sau thông tin được sử dụng
   (Ví dụ: [Nguồn: file_abc.pdf, Trang: 10]).
```

### 6.3 Grounding in Context

```python
# Trong user prompt
[TÀI LIỆU THAM KHẢO]
--- Tài liệu 1 ---
Nguồn: blld.pdf | Trang: 46
Nội dung:
Điều 139. Nghỉ thai sản...

# LLM must base answer on this context
```

---

## 7. Context Formatting

### 7.1 format_context Function

```python
# src/rag_engine/prompts.py

def format_context(documents: List[Document]) -> str:
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        raw_page = doc.metadata.get("page", "N/A")
        
        # Convert 0-based to 1-based page number
        try:
            page = int(raw_page) + 1
        except:
            page = raw_page

        content = doc.page_content.strip()
        
        context_parts.append(
            f"--- Tài liệu {i} ---\n"
            f"Nguồn: {source} | Trang: {page}\n"
            f"Nội dung:\n{content}\n"
        )
    
    return "\n".join(context_parts)
```

### 7.2 Output Example

```
--- Tài liệu 1 ---
Nguồn: luat_lao_dong.pdf | Trang: 46
Nội dung:
Điều 139. Nghỉ thai sản
1. Lao động nữ được nghỉ trước và sau khi sinh con là 6 tháng...

--- Tài liệu 2 ---
Nguồn: nghi_dinh_145.pdf | Trang: 12
Nội dung:
Điều 15. Chế độ nghỉ khi vợ sinh con...
```

---

## 8. Prompt Variations

### 8.1 General Chat Prompt

```python
GENERAL_SYSTEM_PROMPT = """Bạn là Trợ lý Pháp luật AI chuyên về luật lao động Việt Nam.
Người dùng vừa đưa ra một câu hỏi hoặc câu chào xã giao.

Nhiệm vụ:
1. Dựa vào [LỊCH SỬ TRÒ CHUYỆN] để hiểu ngữ cảnh.
2. Phản hồi lịch sự, thân thiện, ngắn gọn.
3. Cuối cùng, LUÔN hướng người dùng quay lại chủ đề pháp luật."""
```

### 8.2 Query Rewriting Prompt

```python
CONDENSE_QUESTION_PROMPT = """Bạn là một chuyên gia ngôn ngữ.
Nhiệm vụ: Viết lại câu hỏi thành câu ĐỘC LẬP.

YÊU CẦU:
1. KHÔNG trả lời câu hỏi. CHỈ viết lại.
2. Thay thế đại từ bằng danh từ cụ thể từ lịch sử."""
```

---

## 9. Temperature Settings

### 9.1 Trong dự án

| Component | Temperature | Rationale |
|-----------|-------------|-----------|
| Generator | 0.3 | Some creativity in language |
| Router | 0.0 | Deterministic classification |
| Rewriter | 0.0 | Accurate reformulation |

### 9.2 Code

```python
# Main Generator
self.llm = LLMFactory.create_llm(
    ..., temperature=0.3
)

# Router
self.router_llm = LLMFactory.create_llm(
    ..., temperature=0.0  # Strictly LEGAL or GENERAL
)

# Rewriter
self.rewriter_llm = LLMFactory.create_llm(
    ..., temperature=0.0  # Accurate rewriting
)
```

---

## 10. Prompt Debugging

### 10.1 Logging

```python
logger.info(f"Original: '{query}' -> Standalone: '{standalone_query}'")
logger.info(f"Query Intent: {intent} | Query: '{standalone_query}'")
```

### 10.2 UI Debug Mode

```python
# app.py - Show standalone query
if standalone and standalone != prompt:
    with st.expander("🧠 Tư duy ngữ cảnh"):
        st.info(f"AI đã hiểu: **{standalone}**")
```

---

## 11. Common Prompt Issues

### 11.1 Hallucination

**Vấn đề**: LLM bịa thông tin
**Giải pháp**: Explicit constraints + mandatory citations

### 11.2 Ignoring Context

**Vấn đề**: LLM trả lời từ training data
**Giải pháp**: "CHỈ sử dụng thông tin từ Context"

### 11.3 Wrong Format

**Vấn đề**: LLM không follow structure
**Giải pháp**: Explicit format in user prompt

```python
[YÊU CẦU TRẢ LỜI]
Hãy trả lời theo cấu trúc sau:
### 1. Căn cứ pháp lý
### 2. Nội dung tư vấn
### 3. Kết luận
```

---

## 12. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **Persona + Constraints**: Định nghĩa rõ AI là ai và không được làm gì
> 2. **IRAC Structure**: Format chuẩn cho legal responses
> 3. **Chain-of-Thought**: Hướng dẫn LLM suy nghĩ từng bước
> 4. **Mandatory Citations**: Chống hallucination bằng yêu cầu trích nguồn

---

## Tài liệu liên quan
- [Intent Routing](./02_intent_routing.md)
- [LLM Factory Pattern](./04_llm_factory_pattern.md)
