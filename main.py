import streamlit as st
from dotenv import load_dotenv
import os

# Import các thành phần cốt lõi
from core.llm_factory import LLMFactory
from core.orchestrator import Orchestrator

# 1. Cấu hình giao diện và load biến môi trường
load_dotenv()
st.set_page_config(page_title="AI Tiệm Vàng - Enterprise Agent", layout="wide")

# --- HÀM KHỞI TẠO HỆ THỐNG ---
def init_system(provider):
    """Khởi tạo bộ não của hệ thống dựa trên nhà cung cấp được chọn"""
    try:
        # LLMFactory sẽ tự động lấy API Key từ .env tương ứng với provider
        llm = LLMFactory.get_model(provider)
        # Khởi tạo bộ điều phối
        return Orchestrator(llm)
    except Exception as e:
        st.error(f"Lỗi khởi tạo hệ thống: {str(e)}")
        return None

# --- GIAO DIỆN NGƯỜI DÙNG (UI) ---

st.title("🤖 Trợ Lý AI Tiệm Vàng Đa Nghiệp Vụ")
st.markdown("---")

# Sidebar cấu hình
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    
    # Bổ sung chọn nhà cung cấp LLM
    selected_provider = st.selectbox(
        "Chọn não bộ AI (LLM Provider):",
        options=["Gemini", "Groq", "Ollama"],
        index=0,
        help="Gemini/Groq yêu cầu Internet, Ollama chạy Offline trên máy cục bộ."
    )
    
    # Nút cập nhật hệ thống khi đổi Provider hoặc Re-index dữ liệu
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Áp dụng AI"):
            st.session_state.orchestrator = init_system(selected_provider)
            st.success(f"Đã chuyển sang {selected_provider}!")
    with col2:
        if st.button("🔄 Re-index"):
            st.cache_resource.clear()
            st.success("Đã làm mới dữ liệu!")

    st.divider()
    st.info("Chế độ: **Hybrid Mode** (File/DB/API Auto-detect)")

# Khởi tạo bộ não lần đầu (Nếu chưa có trong session_state)
if "orchestrator" not in st.session_state:
    with st.spinner(f"Đang khởi động Agent với {selected_provider}..."):
        st.session_state.orchestrator = init_system(selected_provider)

# Quản lý lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LUỒNG XỬ LÝ CHÍNH ---

if prompt := st.chat_input("Hỏi tôi về giá vàng, chính sách cầm đồ hoặc bảo hành..."):
    # 1. Hiển thị câu hỏi của khách
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Agent xử lý (Tìm nghiệp vụ -> Kết nối dữ liệu -> Suy luận)
    with st.chat_message("assistant"):
        if st.session_state.orchestrator is None:
            st.error("Hệ thống chưa được khởi tạo. Vui lòng kiểm tra cấu hình .env và chọn lại AI.")
        else:
            with st.spinner(f"AI ({selected_provider}) đang xử lý..."):
                try:
                    # Gọi bộ điều phối để xử lý câu hỏi
                    response = st.session_state.orchestrator.handle_request(prompt)
                    st.markdown(response)
                    
                    # Lưu vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {str(e)}")