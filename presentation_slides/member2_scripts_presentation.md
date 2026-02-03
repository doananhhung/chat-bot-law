    # Script Thuyết Trình - Member 2 (Hiệp)
    ## Chủ đề: Data Ingestion & Vector Database

    ---

    ## Slide 1: Section Title - Data Ingestion & Vector Database

    **Thời lượng: 30 giây**

    > "Xin chào mọi người, phần tiếp theo em sẽ trình bày về **Data Ingestion và Vector Database** - tức là quá trình **chuyển đổi từ file PDF thành một cơ sở tri thức có thể tìm kiếm được**."
    >
    > "Đây là bước nền tảng quan trọng nhất của hệ thống RAG, vì nếu không có dữ liệu được xử lý tốt thì LLM sẽ không có thông tin để trả lời câu hỏi."

    ---

    ## Slide 2: 4-Step Ingestion Pipeline

    **Thời lượng: 1 phút**

    > "Toàn bộ quá trình ingestion có thể tóm gọn trong **4 bước** như sơ đồ này:"
    >
    > 1. **LOAD**: Đọc file PDF/DOCX thành văn bản thuần túy - sử dụng module `loader.py`
    > 2. **SPLIT**: Chia văn bản thành các **chunks nhỏ** - sử dụng module `splitter.py`
    > 3. **EMBED**: Chuyển đổi mỗi chunk thành **vector số** 768 chiều - sử dụng module `indexer.py`
    > 4. **STORE**: Lưu trữ các vectors vào **FAISS** để tìm kiếm nhanh
    >
    > "Mỗi bước này đều có một module riêng biệt, đảm bảo code dễ bảo trì và test."

    ---

    ## Slide 3: Document Loader

    **Thời lượng: 1 phút 30 giây**

    > "Đầu tiên là **Document Loader** - module chịu trách nhiệm đọc file."
    >
    > "Hệ thống hỗ trợ 2 định dạng chính:"
    > - **.pdf**: Sử dụng **PyPDFLoader** từ thư viện `pypdf` - loader này đọc từng trang PDF và trả về văn bản
    > - **.docx**: Sử dụng **Docx2txtLoader** từ thư viện `docx2txt`
    >
    > "Ở bên phải là cấu trúc **Document** mà loader trả về. Mỗi document có 2 phần:"
    > - `page_content`: Nội dung văn bản thực tế, ví dụ 'Điều 139. Nghỉ thai sản...'
    > - `metadata`: Thông tin bổ sung như **source** (tên file gốc) và **page** (số trang)
    >
    > "**Metadata rất quan trọng** - nó cho phép hệ thống trích dẫn nguồn chính xác khi trả lời. Khi LLM trả lời 'Theo Điều 139 Luật Lao động, trang 45', thông tin này lấy từ metadata."
    >
    > "Trong code thực tế, class `DocumentLoader` còn có method `load_documents` để đọc tất cả file trong một thư mục cùng lúc."

    ---

    ## Slide 4: Why Chunking?

    **Thời lượng: 1 phút**

    > "Tại sao cần phải chia nhỏ văn bản thành chunks?"
    >
    > "Có 3 lý do chính:"
    >
    > 1. **LLM Context Limit**: Các LLM có giới hạn số tokens xử lý được, thường khoảng 32K tokens. Một văn bản luật dài có thể vượt quá giới hạn này.
    >
    > 2. **Search Precision**: Chunks nhỏ giúp tìm kiếm chính xác hơn. Thay vì trả về cả một văn bản 100 trang, hệ thống có thể trả về đúng đoạn 1000 ký tự chứa câu trả lời.
    >
    > 3. **Noise Reduction**: Chỉ lấy phần thực sự liên quan đến câu hỏi, không đưa thông tin thừa vào context.
    >
    > "Như hình minh họa, một document 5000 ký tự sẽ được chia thành 5 chunks, mỗi chunk khoảng 1000 ký tự. Lưu ý có **overlap 200 ký tự** giữa các chunks để không mất ngữ cảnh ở điểm cắt."

    ---

    ## Slide 5: Text Splitter

    **Thời lượng: 1 phút 30 giây**

    > "Module `splitter.py` sử dụng **RecursiveCharacterTextSplitter** từ LangChain."
    >
    > "Có 2 tham số quan trọng:"
    > - `chunk_size = 1000`: Mỗi chunk tối đa **1000 ký tự**
    > - `chunk_overlap = 200`: **Overlap 200 ký tự** giữa các chunks liên tiếp
    >
    > "Tham số thứ 3 là `separators` - danh sách ưu tiên vị trí cắt:"
    >
    > | Ưu tiên | Separator | Ý nghĩa |
    > |---------|-----------|---------|
    > | 1 | `\n\n` | Paragraph break - ưu tiên cao nhất |
    > | 2 | `\n` | Line break |
    > | 3 | ` ` (space) | Khoảng trắng |
    > | 4 | `""` | Cắt theo ký tự - fallback cuối cùng |
    >
    > "**Nguyên tắc**: Splitter sẽ cố gắng cắt ở vị trí tự nhiên nhất - ưu tiên giữa các đoạn văn, rồi mới đến giữa dòng, rồi mới đến giữa từ."
    >
    > "Việc này giúp bảo toàn ngữ nghĩa của văn bản sau khi chia."

    ---

    ## Slide 6: What is Embedding?

    **Thời lượng: 1 phút**

    > "Bước tiếp theo là **Embedding** - chuyển đổi văn bản thành vector số."
    >
    > "Sơ đồ này mô tả quá trình:"
    >
    > 1. **Input**: Một đoạn văn bản tiếng Việt, ví dụ 'Thai sản được nghỉ bao nhiêu ngày?'
    >
    > 2. **Embedding Model**: Sử dụng model **vietnamese-bi-encoder** - một model được train đặc biệt cho tiếng Việt
    >
    > 3. **Output**: Một **vector số** với 768 chiều, ví dụ `[0.12, -0.34, 0.56, ..., 0.78]`
    >
    > "Vector này **encode ngữ nghĩa** của văn bản. Hai câu có ý nghĩa tương tự sẽ có vector gần nhau trong không gian 768 chiều, ngay cả khi từ ngữ khác nhau."
    >
    > "Đây là cốt lõi của **semantic search** - tìm kiếm theo nghĩa, không phải theo từ khóa."

    ---

    ## Slide 7: vietnamese-bi-encoder

    **Thời lượng: 1 phút**

    > "Model embedding em chọn là **vietnamese-bi-encoder** từ BKAI Foundation Models."
    >
    > "Một số thông số quan trọng:"
    > - **Type**: Bi-Encoder - encode mỗi document một lần, sau đó chỉ cần embed query và so sánh vector
    > - **Dimensions**: 768 chiều - đủ phong phú để capture ngữ nghĩa tiếng Việt
    > - **Language**: Được tối ưu đặc biệt cho tiếng Việt
    >
    > "Trong code, em sử dụng **HuggingFaceEmbeddings** từ LangChain với tham số:"
    > - `model_name`: Tên model trên HuggingFace
    > - `device = 'cpu'`: Chạy trên CPU thay vì GPU
    > - `normalize_embeddings = True`: Chuẩn hóa vector để tính cosine similarity
    >
    > "**Bi-Encoder** có lợi thế là encode documents chỉ **một lần** khi build index. Khi search, chỉ cần embed query mới, nên rất nhanh."

    ---

    ## Slide 8: FAISS Vector Search

    **Thời lượng: 1 phút**

    > "Sau khi có vectors, cần một hệ thống để **lưu trữ và tìm kiếm** nhanh. Đó là **FAISS** - Facebook AI Similarity Search."
    >
    > "FAISS được phát triển bởi Meta AI Research, chuyên dụng cho việc tìm kiếm similarity trong không gian vector nhiều chiều."
    >
    > "Flow tìm kiếm như sau:"
    > 1. Query của user được **embed** thành vector
    > 2. FAISS search **Top-10 vectors gần nhất** với query vector
    > 3. Trả về các documents tương ứng
    >
    > "Ví dụ: Query 'nghỉ thai sản mấy tháng?' sẽ được embed thành vector `[0.1, 0.2, ..., 0.8]`, sau đó FAISS tìm các documents có vector gần nhất - kết quả là các đoạn về Điều 139, về thai sản..."

    ---

    ## Slide 9: FAISS Index Types

    **Thời lượng: 1 phút 30 giây**

    > "FAISS có nhiều loại index khác nhau. Slide này so sánh 2 loại chính: **Flat Index** và **IVF Index**."
    >
    > "**Flat Index** (bên trái):"
    > - Là **Exact Search** - tìm kiếm chính xác
    > - So sánh query với **TẤT CẢ** vectors trong database
    > - Ưu điểm: **Accuracy 100%** - không bao giờ miss kết quả tốt
    > - Nhược điểm: Chậm khi dữ liệu lớn - **O(N)** complexity
    >
    > "**IVF Index** (bên phải):"
    > - Là **Approximate Search** - tìm kiếm xấp xỉ
    > - Chia vectors thành các **clusters**, chỉ search trong một số clusters
    > - Ưu điểm: **5-10x nhanh hơn**, **O(log N)** complexity
    > - Nhược điểm: Accuracy khoảng **~97%** - có thể miss một vài kết quả
    >
    > "Đây là **trade-off** giữa speed và accuracy. Với dataset nhỏ, dùng Flat. Với dataset lớn, IVF là lựa chọn tốt hơn."

    ---

    ## Slide 10: IVF Training Process - K-means Clustering

    **Thời lượng: 1 phút 30 giây**

    > "IVF hoạt động dựa trên **K-means clustering**. Sơ đồ này mô tả quá trình **training** của IVF index."
    >
    > "Có 4 giai đoạn:"
    >
    > 1. **INPUT DATA**: Tất cả embedding vectors từ documents, ví dụ 1500 vectors với 768 dimensions
    >
    > 2. **TRAINING PHASE**: 
    >    - Chạy thuật toán **K-means** để tìm **64 cluster centers** (nlist = 64)
    >    - Mỗi cluster center gọi là **centroid**
    >
    > 3. **ASSIGNMENT**:
    >    - Gán mỗi vector vào cluster có centroid gần nhất
    >
    > 4. **RESULT**: Một **IVF Index đã trained**, sẵn sàng để search
    >
    > "Training chỉ chạy **một lần** khi build index. Sau đó, search sẽ rất nhanh vì chỉ cần tìm trong một số clusters thay vì tất cả vectors."

    ---

    ## Slide 11: IVF Training Details

    **Thời lượng: 1 phút 30 giây**

    > "Chi tiết hơn về thuật toán K-means trong IVF:"
    >
    > "**K-means Steps:**"
    > 1. **Initialize**: Chọn 64 điểm ngẫu nhiên làm centroids ban đầu
    > 2. **Assign**: Gán mỗi vector vào centroid gần nhất
    > 3. **Update**: Tính lại centroid = trung bình của các vectors trong cluster
    > 4. **Repeat**: Lặp lại 2-3 cho đến khi converge (centroids không thay đổi nhiều)
    >
    > "**Training Cost:**"
    > - Chỉ chạy **1 lần** khi build index
    > - Khoảng **10-30 iterations** để converge
    > - Time complexity: **O(N × K × D × iterations)**
    >
    > "Bên phải là code configuration:"
    > - `IVF_NLIST = 64`: Số clusters
    > - `IVF_NPROBE = 8`: Số clusters sẽ search khi query
    > - Factory string: `IVF64,Flat` - tạo index với 64 clusters
    >
    > "**Rule of thumb** cho nlist: nên đặt **√N** với N là số vectors. Với 1500 vectors, √1500 ≈ 39, nên 64 là hợp lý."

    ---

    ## Slide 12: IVF Search Process (nprobe=8)

    **Thời lượng: 1 phút**

    > "Khi có query, quá trình **search trong IVF** diễn ra như sau:"
    >
    > 1. **QUERY**: Query được embed thành vector
    >
    > 2. **DISTANCE TO CENTROIDS**: Tính khoảng cách từ query vector đến **64 centroids**
    >
    > 3. **SELECT TOP-K CLUSTERS**: Chọn **8 clusters gần nhất** (nprobe = 8)
    >    - Đây là điểm khác biệt với Flat - chỉ search 8/64 = 12.5% data
    >
    > 4. **SEARCH IN CLUSTERS**: Search chỉ trong vectors thuộc 8 clusters đó
    >
    > 5. **RESULT**: Trả về **Top-10 documents** tương tự nhất
    >
    > "nprobe càng cao, accuracy càng cao nhưng chậm hơn. nprobe = 64 (full) sẽ tương đương Flat index."

    ---

    ## Slide 13: IVF Performance Benchmark

    **Thời lượng: 1 phút 30 giây**

    > "Đây là **benchmark thực tế** em đã chạy trên dataset Vietnamese Labor Law."
    >
    > "**Test Setup:**"
    > - Dataset: Vietnamese Labor Law
    > - Total vectors: ~1,500 chunks
    > - Hardware: CPU Intel i7
    > - Query set: 100 legal questions
    >
    > "**Results:**"
    >
    > | Index | Config | Search Time | Recall@10 |
    > |-------|--------|-------------|-----------|
    > | Flat | - | 45ms | 100% |
    > | IVF64 | nprobe=4 | 12ms | 95.2% |
    > | IVF64 | nprobe=8 | 18ms | 97.8% |
    > | IVF64 | nprobe=16 | 28ms | 99.1% |
    >
    > "**Key Findings:**"
    > - IVF với nprobe=8: **2.5x nhanh hơn** Flat với **~98% accuracy** - đây là **best trade-off**
    > - Memory overhead chỉ ~7% cho 64 centroids
    > - Training time: ~2 giây cho 1,500 vectors
    >
    > "Với dataset hiện tại 1,500 vectors, Flat vẫn đủ nhanh. Nhưng với 10K+ vectors, IVF sẽ cần thiết."

    ---

    ## Slide 14: When to Use IVF?

    **Thời lượng: 1 phút**

    > "**Khi nào nên dùng IVF?**"
    >
    > "✅ **Sử dụng IVF khi:**"
    > - Dataset **> 10,000 vectors**
    > - Cần **low latency** (< 50ms)
    > - Chấp nhận được **~2-3% recall loss**
    > - Production environment với nhiều queries
    >
    > "❌ **Dùng Flat khi:**"
    > - Dataset nhỏ (< 10,000)
    > - Cần **100% accuracy** - không được miss kết quả nào
    > - Development/testing - ưu tiên đúng hơn nhanh
    >
    > "**Dự án này:** 1,500 vectors → có thể dùng Flat, nhưng em chọn IVF để **demo scalability** - cho thấy hệ thống có thể scale được."
    >
    > "Trade-off equation: `Speed_gain = N / (nlist × nprobe)`, `Accuracy_loss ≈ 2-5%`"

    ---

    ## Slide 15: Incremental Sync Flow

    **Thời lượng: 2 phút**

    > "Bây giờ em sẽ trình bày về **Incremental Sync** - tức là cách hệ thống đồng bộ khi có thay đổi."
    >
    > "Thay vì rebuild toàn bộ index mỗi khi thêm/sửa file (rất tốn thời gian), hệ thống sử dụng **differential update**."
    >
    > "Sơ đồ có 4 giai đoạn:"
    >
    > "**1. SCAN PHASE:**"
    > - Scan thư mục `data/raw/` để liệt kê tất cả files
    > - Load `indexing_metadata.json` - file tracking trạng thái trước đó
    > - Tính **MD5 hash** cho mỗi file hiện tại
    >
    > "**2. CLASSIFICATION:**"
    > - So sánh hash hiện tại với hash trong metadata
    > - Phân loại: **New** (file mới), **Modified** (hash khác), **Deleted** (không còn trên disk), **Unchanged** (hash giống)
    >
    > "**3. PROCESSING:**"
    > - **Deleted/Modified**: Delete old chunks từ FAISS index
    > - **New/Modified**: Load → Split → Embed → Add to index
    > - **Unchanged**: Skip - không làm gì
    >
    > "**4. SAVE:**"
    > - Save FAISS index (faiss + pkl files)
    > - Save metadata.json với hash và chunk_ids mới
    >
    > "Kết quả: Chỉ xử lý những gì thay đổi, tiết kiệm rất nhiều thời gian so với rebuild toàn bộ."

    ---

    ## Slide 16: Data Structure - Folder Layout

    **Thời lượng: 1 phút**

    > "Để hiểu rõ hơn, em sẽ giải thích **cấu trúc thư mục** của dữ liệu."
    >
    > "Có 2 thư mục chính:"
    >
    > "**data/raw/**"
    > - Chứa tài liệu nguồn: `luat_lao_dong.pdf`, `bo_luat_dan_su.pdf`
    > - Đây là input của pipeline
    >
    > "**data/vector_store/**"
    > - `index.faiss`: Chứa các embedding vectors (dữ liệu số)
    > - `index.pkl`: Chứa nội dung văn bản gốc (để hiển thị kết quả)
    > - `indexing_metadata.json`: Theo dõi trạng thái file (hash, chunk IDs)
    >
    > "**Mục đích:** Tách biệt file nguồn và dữ liệu đã xử lý. Khi update, chỉ cần thêm/sửa file trong `raw/`, sau đó run sync command."

    ---

    ## Slide 17: Data Structure - Metadata JSON

    **Thời lượng: 1 phút**

    > "File **indexing_metadata.json** là 'brain' của incremental sync."
    >
    > "Cấu trúc:"
    > ```json
    > {
    >   "last_updated": "2026-01-27T10:30:15Z",
    >   "files": {
    >     "luat_lao_dong.pdf": {
    >       "hash": "a1b2c3d4e5f6g7h8...",
    >       "last_modified": 1706353815.234,
    >       "chunk_ids": ["a1b2c3d4_0", "a1b2c3d4_1", "a1b2c3d4_2"]
    >     }
    >   }
    > }
    > ```
    >
    > "**Các trường quan trọng:**"
    > - `hash`: **MD5 hash** của nội dung file - dùng để phát hiện thay đổi
    > - `chunk_ids`: Danh sách IDs của vectors trong FAISS - dùng để xóa khi file bị delete/update
    >
    > "Nhờ có chunk_ids, khi một file thay đổi, hệ thống biết chính xác cần xóa chunks nào trong index."

    ---

    ## Slide 18: Data Structure - index.faiss

    **Thời lượng: 1 phút**

    > "**index.faiss** là file binary chứa các vectors."
    >
    > "Cấu trúc bên trong:"
    >
    > "**FAISS Index Metadata:**"
    > - Index Type: IVFFlat hoặc Flat
    > - Dimension: 768 (phải match với embedding model)
    > - Total vectors: 1,500
    > - nlist: 64 (số clusters nếu dùng IVF)
    >
    > "**Vector Data:**"
    > - Mỗi vector có ID (như `a1b2c3d4_0`)
    > - Mỗi vector là array 768 số float, ví dụ `[0.123, -0.456, 0.789, ...]`
    >
    > "File này khoảng **4.5 MB** cho 1,500 vectors."
    >
    > "**Chức năng:** Cho phép tìm kiếm similarity nhanh bằng phép toán vector (dot product, L2 distance)."

    ---

    ## Slide 19: Data Structure - index.pkl

    **Thời lượng: 1 phút**

    > "**index.pkl** là file Pickle chứa **văn bản gốc** của mỗi chunk."
    >
    > "Cấu trúc:"
    >
    > "**docstore:**"
    > - Key: chunk_id (như `a1b2c3d4_0`)
    > - Value: Document object với:
    >   - `page_content`: Nội dung text, ví dụ 'Điều 139. Nghỉ thai sản...'
    >   - `metadata`: source, page, chunk_id
    >
    > "**index_to_docstore_id:**"
    > - Mapping từ FAISS index position (0, 1, 2...) → chunk_id
    > - Khi FAISS trả về index position 0, lookup mapping để lấy chunk_id, rồi lấy Document từ docstore
    >
    > "File này khoảng **2.1 MB**."
    >
    > "**Chức năng:** Sau khi FAISS tìm được vectors gần nhất, cần lấy văn bản gốc từ đây để hiển thị cho user."

    ---

    ## Tổng kết

    **Thời lượng: 1 phút**

    > "Để tổng kết phần Data Ingestion & Vector Database:"
    >
    > "**4-Step Pipeline:**"
    > 1. **Load**: PyPDFLoader/Docx2txtLoader
    > 2. **Split**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
    > 3. **Embed**: vietnamese-bi-encoder (768 dimensions)
    > 4. **Store**: FAISS (Flat hoặc IVF)
    >
    > "**Key Design Decisions:**"
    > - Sử dụng **model tiếng Việt** để embedding chính xác hơn
    > - **IVF index** cho scalability khi dataset lớn
    > - **Incremental sync** với MD5 hash tracking để update hiệu quả
    > - **Chunk IDs** cho phép delete/update chính xác từng chunk
    >
    > "Cảm ơn mọi người đã lắng nghe. Giờ em sẽ chuyển sang phần demo hoặc Q&A."

    ---

    ## Thời gian ước tính
    - **Tổng:** ~20 phút
    - Có thể điều chỉnh tùy thời gian presentation thực tế
