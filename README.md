🤖 Tiệm Vàng AI - Enterprise Multi-Agent System (Chatbot\_4)📝 1. Tổng quan dự ánChatbot\_4 là hệ thống trợ lý ảo thông minh cấp độ doanh nghiệp dành cho ngành kim hoàn.Hệ thống giải quyết bài toán quản trị dữ liệu phân tán bằng kiến trúc Hybrid Data-Source Adaptation, cho phép tự động điều phối linh hoạt giữa các nguồn dữ liệu từ File Local (Excel/PDF) đến các hệ thống Database/API Backend.Mục tiêu: Quản lý và vận hành 100+ nghiệp vụ trên một nền tảng AI duy nhất mà không cần thay đổi mã nguồn cốt lõi khi mở rộng.🏗 2. Kiến trúc \& Luồng dữ liệu (Data Workflow)Hệ thống hoạt động theo mô hình Agentic RAG, tự động lựa chọn công cụ phù hợp thông qua các lớp xử lý thông minh.Quy trình xử lý:Input: Khách hàng đặt câu hỏi qua giao diện Streamlit.Routing: router.py sử dụng Vector Similarity để xác định nghiệp vụ trong 100+ Task đã đăng ký.Connecting: connector.py kiểm tra cấu hình để quyết định gọi dữ liệu từ File, DB hay API.Retrieving: Các Engine chuyên biệt trích xuất dữ liệu (Context).Reasoning: LLM (Gemini/Groq) tiếp nhận Context và biên soạn câu trả lời.📂 3. Cấu trúc chi tiết dự án (Project Structure)PlaintextChatbot\_4/

├── main.py                 # Điểm khởi chạy giao diện (Streamlit Dashboard)

├── requirements.txt        # Danh sách thư viện cần cài đặt

├── .env                    # Lưu trữ API Key bảo mật (Gemini, Groq,...)

│

├── core/                   # BỘ NÃO ĐIỀU PHỐI (ORCHESTRATION)

│   ├── llm\_factory.py      # Quản lý cấu hình và đổi não AI (Gemini/Groq/Ollama)

│   ├── orchestrator.py     # Tiếp nhận câu hỏi, điều phối các Engine chạy song song

│   ├── connector.py        # Bộ chuyển mạch thông minh: Tự chọn File, DB hoặc API

│   └── registry.py         # Danh mục quản lý 100+ nghiệp vụ và mô tả Task

│

├── engines/                # CÁC BỘ MÁY TRUY XUẤT (DATA ENGINES)

│   ├── base\_engine.py      # Lớp mẫu trừu tượng (Interface) cho mọi Engine

│   ├── sql\_engine.py       # Chuyên gia số liệu: Xử lý file Excel hoặc Database SQL

│   ├── api\_engine.py       # Chuyên gia kết nối: Gọi RESTful API từ Backend

│   └── vector\_engine.py    # Chuyên gia tri thức: Tìm kiếm ngữ nghĩa trong Word/PDF

│

├── utils/                  # CÔNG CỤ BỔ TRỢ

│   └── router.py           # Bộ định tuyến Semantic: Phân loại câu hỏi vào đúng Task

│

├── config/                 # CẤU HÌNH HỆ THỐNG

│   └── settings.yaml       # Nơi bật/tắt chế độ File/DB/API không cần sửa code

│

└── data/                   # KHO DỮ LIỆU NỘI BỘ (LOCAL STORAGE)

&nbsp;   ├── training/           # Chứa file văn bản (.docx, .pdf) cho Vector Search

&nbsp;   └── database/           # Chứa file số liệu (.xlsx, .csv) cho SQL Engine

🛠 4. Danh sách thư viện (requirements.txt)Plaintext# --- UI \& Environment ---

streamlit             # Giao diện người dùng Web

python-dotenv         # Quản lý biến môi trường .env

pydantic-settings     # Quản lý cấu hình linh động



\# --- AI Framework ---

langchain             # Framework quản lý Agent

langchain-google-genai # Kết nối Google Gemini

langchain-groq        # Kết nối Groq (Llama 3)

langchain-community   # Công cụ hỗ trợ cộng đồng



\# --- Data \& Connectors ---

pandas                # Xử lý Excel, CSV

openpyxl              # Đọc/Ghi file Excel

sqlalchemy            # Kết nối Database (MySQL, Postgres,...)

pymysql               # Driver cho MySQL

requests              # Gọi API Backend



\# --- Vector Search (RAG) ---

faiss-cpu             # Cơ sở dữ liệu Vector siêu nhanh

sentence-transformers # Chuyển văn bản thành Vector (Embedding)

python-docx           # Trích xuất dữ liệu file Word

pypdf                 # Trích xuất dữ liệu file PDF



\# --- Concurrency ---

asyncio               # Xử lý đa luồng, chạy song song các Engine

🚀 5. Hướng giải quyết cho 100+ Nghiệp vụVấn đềGiải pháp triển khaiQuy mô lớnSử dụng registry.py để quản lý Task dưới dạng Plugin. Thêm Task mới không ảnh hưởng Task cũ.Nguồn dữ liệu hỗn hợpconnector.py tự động chuyển đổi giữa File/DB/API dựa trên cấu hình settings.yaml.Tốc độ phản hồiÁp dụng Asyncio để các Engine truy vấn dữ liệu song song thay vì tuần tự.Độ chính xácSemantic Router giúp lọc đúng dữ liệu cần thiết, tránh nạp quá nhiều thông tin dư thừa cho AI.💻 6. Hướng dẫn cài đặtClone dự án:Bashgit clone https://github.com/VuNghiXuan/chatbot\_4.git

cd chatbot\_4

Cài đặt thư viện:Bashpip install -r requirements.txt

Cấu hình API:Dán API Key vào file .env hoặc nhập trực tiếp trên UI.Khởi chạy:Bashstreamlit run main.py

Phát triển bởi: VuNghiXuan - 2026

