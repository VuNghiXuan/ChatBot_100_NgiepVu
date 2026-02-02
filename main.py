import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3
import asyncio  # Bổ sung thư viện này để chạy Async

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
        # LLMFactory tự động lấy API Key từ .env tương ứng với provider
        llm = LLMFactory.get_model(provider)
        # Khởi tạo bộ điều phối (Đã bao gồm lưu trữ DB bên trong)
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
    
    selected_provider = st.selectbox(
        "Chọn não bộ AI (LLM Provider):",
        options=["Gemini", "Groq", "Ollama"],
        index=0,
        help="Gemini/Groq yêu cầu Internet, Ollama chạy Offline trên máy cục bộ."
    )
    
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
    
    if st.button("🗑 Xóa lịch sử Chat"):
        st.session_state.messages = []
        st.rerun()

# Khởi tạo bộ não lần đầu
if "orchestrator" not in st.session_state:
    with st.spinner(f"Đang khởi động Agent với {selected_provider}..."):
        st.session_state.orchestrator = init_system(selected_provider)

# Quản lý lịch sử chat (UI)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout chia cột
chat_col, log_col = st.columns([2, 1])

with chat_col:
    st.subheader("💬 Trò chuyện")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Luồng xử lý chính
    if prompt := st.chat_input("Hỏi tôi về giá vàng, chính sách cầm đồ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.orchestrator is None:
                st.error("Hệ thống chưa được khởi tạo. Kiểm tra .env!")
            else:
                with st.spinner(f"AI ({selected_provider}) đang xử lý..."):
                    try:
                        # QUAN TRỌNG: Gọi handle_request thông qua asyncio.run
                        # vì hàm này đã được chuyển thành async def trong orchestrator.py
                        response = asyncio.run(st.session_state.orchestrator.handle_request(prompt))
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi: {str(e)}")

with log_col:
    st.subheader("📜 Nhật ký Database")
    # Sử dụng placeholder để UI tự cập nhật mượt mà hơn
    log_placeholder = st.empty()
    try:
        conn = sqlite3.connect("data/database/history.db")
        query = "SELECT timestamp, task_name, user_query FROM chat_history ORDER BY id DESC LIMIT 15"
        df = pd.read_sql_query(query, conn)
        log_placeholder.dataframe(df, use_container_width=True, hide_index=True)
        conn.close()
    except Exception:
        st.write("Chưa có dữ liệu nhật ký.")