"""1. File main.py (Trạm điều khiển trung tâm)"""
import streamlit as st
from dotenv import load_dotenv
import os

# Import các thành phần cốt lõi
from core.llm_factory import LLMFactory
from core.orchestrator import Orchestrator

# 1. Cấu hình giao diện và load biến môi trường
load_dotenv()
st.set_page_config(page_title="AI Tiệm Vàng - Enterprise Agent", layout="wide")

def init_system():
    """Khởi tạo bộ não của hệ thống"""
    # Khởi tạo model AI (Mặc định dùng Gemini)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Thiếu GOOGLE_API_KEY trong file .env hoặc cấu hình!")
        st.stop()
        
    llm = LLMFactory.get_model("Gemini", api_key)
    
    # Khởi tạo bộ điều phối (Đã bao gồm Router và Connector bên trong)
    return Orchestrator(llm)

# --- GIAO DIỆN NGƯỜI DÙNG (UI) ---

st.title("🤖 Trợ Lý AI Tiệm Vàng Đa Nghiệp Vụ")
st.markdown("---")

# Sidebar cấu hình
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    st.info("Hệ thống đang chạy chế độ **Hybrid Mode** (Tự động chuyển đổi File/DB/API)")
    
    if st.button("🔄 Làm mới bộ chỉ mục (Re-index)"):
        st.cache_resource.clear()
        st.success("Đã cập nhật dữ liệu mới nhất từ các nguồn!")

# Khởi tạo bộ não (Sử dụng cache để không khởi động lại mỗi lần chat)
if "orchestrator" not in st.session_state:
    with st.spinner("Đang khởi động bộ não Agent..."):
        st.session_state.orchestrator = init_system()

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
        with st.spinner("AI đang truy xuất dữ liệu..."):
            try:
                # Gọi bộ điều phối để xử lý câu hỏi
                response = st.session_state.orchestrator.handle_request(prompt)
                st.markdown(response)
                
                # Lưu vào lịch sử
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Đã xảy ra lỗi hệ thống: {str(e)}"
                st.error(error_msg)