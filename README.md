# ChatBot_100_NgiepVu
🤖 Tiệm Vàng AI - Enterprise Multi-Agent System (Chatbot_4)
📝 1. Mô tả dự án
Hệ thống Chatbot_4 là một trợ lý ảo thông minh đa nghiệp vụ dành cho ngành kim hoàn. Điểm khác biệt cốt lõi là kiến trúc Hybrid Data-Source Adaptation, cho phép hệ thống tự động nhận diện và kết nối linh hoạt giữa các nguồn dữ liệu từ thô (File Excel/Word) đến các hệ thống quản trị hiện đại (Database/API Backend).

Hệ thống được thiết kế để giải quyết bài toán: "Làm sao để AI hiểu và xử lý 100+ nghiệp vụ từ nhiều nguồn dữ liệu khác nhau mà không cần sửa đổi mã nguồn gốc?"

🏗 2. Kiến trúc & Hướng giải quyết linh động
A. Cơ chế Tự động kết nối (Smart Connector)
Hệ thống không cố định nguồn dữ liệu. Thay vào đó, nó sử dụng lớp SmartConnector để kiểm tra môi trường:

Ưu tiên 1 (API): Nếu có Endpoint API, Agent sẽ gọi Backend để lấy dữ liệu thực tế.

Ưu tiên 2 (Database): Nếu có chuỗi kết nối SQL, Agent tự viết truy vấn vào DB.

Ưu tiên 3 (File): Nếu không có kết nối mạng, Agent tự lục trong kho file local (data/).

B. Định tuyến nghiệp vụ bằng Vector (Semantic Routing)
Để quản lý 100+ nghiệp vụ:

Hệ thống chuyển đổi "Mô tả nghiệp vụ" thành các Vector không gian.

Khi khách hỏi, AI so sánh Vector câu hỏi với 100 Vector nghiệp vụ để chọn ra "nhân viên" (Engine) phù hợp nhất trong 0.01 giây.

C. Xử lý đa nhiệm song song (Parallel Orchestration)
Với các câu hỏi phức tạp (vừa hỏi giá, vừa hỏi chính sách), AgentManager sẽ kích hoạt đồng thời các Engine liên quan thông qua Asyncio, giúp giảm thời gian phản hồi xuống mức tối thiểu.

📂 3. Cấu trúc thư mục mở rộng
Plaintext
Chatbot_4/
├── core/
│   ├── llm_factory.py     # Quản lý đổi "não" AI (Gemini, Groq, Ollama)
│   ├── orchestrator.py    # Bộ não điều phối đa nhiệm (Parallel Execution)
│   ├── connector.py       # Bộ chuyển mạch tự động (File <-> DB <-> API)
│   └── registry.py        # Danh mục quản lý 100+ nghiệp vụ
├── engines/
│   ├── base_engine.py     # Chuẩn chung cho mọi bộ máy tìm kiếm
│   ├── sql_engine.py      # Xử lý số liệu (Excel & SQL Database)
│   ├── api_engine.py      # Kết nối Backend API RESTful
│   └── vector_engine.py   # Xử lý tri thức văn bản (Word, PDF, FAQ)
├── utils/
│   └── router.py          # Định tuyến thông minh bằng Vector Similarity
├── config/
│   └── settings.yaml      # Cấu hình linh động nguồn dữ liệu
└── main.py                # Dashboard điều khiển (Streamlit)
📚 4. Danh sách thư viện (requirements.txt)
Để hệ thống chạy được cả 3 chế độ (File, DB, API) và hỗ trợ đa nghiệp vụ, anh cần cài đặt các thư viện sau:

Plaintext
# --- Giao diện & Core ---
streamlit             # Giao diện Web Dashboard
pydantic-settings     # Quản lý cấu hình linh động (.env, yaml)
python-dotenv         # Đọc biến môi trường

# --- AI & LLM Framework ---
langchain             # Framework quản lý Agent
langchain-google-genai # Kết nối Gemini
langchain-groq        # Kết nối Groq (Llama 3)
langchain-community   # Các công cụ hỗ trợ cộng đồng

# --- Xử lý Dữ liệu (File & DB) ---
pandas                # Xử lý bảng biểu, Excel, CSV
openpyxl              # Đọc file Excel .xlsx
sqlalchemy            # Kết nối Database (MySQL, Postgres, SQL Server)
pymysql               # Driver cho MySQL
requests              # Gọi API Backend

# --- Xử lý Văn bản & Vector (RAG) ---
faiss-cpu             # Cơ sở dữ liệu Vector siêu nhanh
sentence-transformers # Chuyển văn bản thành Vector (Embedding)
python-docx           # Đọc file Word
pypdf                 # Đọc file PDF
unstructured          # Xử lý dữ liệu văn bản không cấu trúc

# --- Hiệu năng ---
asyncio               # Xử lý đa luồng, chạy song song các Engine
🚀 5. Hướng dẫn mở rộng
Khi có nghiệp vụ thứ 101:

Khai báo tên nghiệp vụ và mô tả vào file cấu hình.

Cung cấp nguồn dữ liệu (ném file vào data/ hoặc cung cấp API endpoint).

Hệ thống sẽ tự động "nhận việc" và tích hợp vào luồng chat mà không cần khởi động lại toàn bộ.

Dự án được thiết kế để chuyển đổi số toàn diện cho tiệm vàng từ thủ công sang tự động hóa bằng AI.
