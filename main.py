import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3
import asyncio
import nest_asyncio

# Khởi tạo nest_asyncio
nest_asyncio.apply()

from core.llm_factory import LLMFactory
from core.orchestrator import Orchestrator

# 1. Cấu hình giao diện
load_dotenv()
st.set_page_config(page_title="AI Tiệm Vàng - Enterprise Agent", layout="wide")

# --- HÀM KHỞI TẠO ---
def init_system(provider):
    try:
        llm = LLMFactory.get_model(provider)
        return Orchestrator(llm)
    except Exception as e:
        st.error(f"Lỗi khởi tạo hệ thống: {str(e)}")
        return None

def on_provider_change():
    new_provider = st.session_state.provider_selector
    st.session_state.orchestrator = init_system(new_provider)

# --- GIAO DIỆN SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    options = ["Ollama", "Gemini", "Groq"]
    st.selectbox(
        "Chọn não bộ AI (LLM Provider):",
        options=options,
        index=0,
        key="provider_selector",
        on_change=on_provider_change
    )
    
    if st.button("🔄 Làm mới dữ liệu (Re-index)", width='stretch'):
        st.cache_resource.clear()
        st.success("Đã làm mới dữ liệu kiến thức!")

    st.divider()
    if st.button("🗑 Xóa lịch sử Chat", width='stretch'):
        st.session_state.messages = []
        st.rerun()

# Khởi tạo mặc định
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = init_system("Ollama")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LAYOUT CHÍNH ---
st.title("🤖 Trợ Lý AI Tiệm Vàng Đa Nghiệp Vụ")
st.markdown("---")

chat_col, log_col = st.columns([2, 1])

with chat_col:
    st.subheader("💬 Trò chuyện")
    
    # Khu vực hiển thị tin nhắn (có thanh cuộn)
    chat_container = st.container(height=600) 
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Nếu là tin nhắn của Assistant, hiển thị kèm nhãn nghiệp vụ nếu có
                if message["role"] == "assistant" and "tasks" in message:
                    tag_html = "".join([f'<span style="background-color: #e1f5fe; color: #01579b; padding: 2px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; margin-right: 5px; border: 1px solid #b3e5fc;">🔍 {t.upper()}</span>' for t in message["tasks"]])
                    st.markdown(tag_html, unsafe_allow_html=True)
                st.markdown(message["content"])

    # Xử lý tin nhắn mới
    if prompt := st.chat_input("Hỏi tôi về giá vàng, chính sách bảo hành..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Hiển thị phản hồi của Assistant
        with chat_container:
            with st.chat_message("assistant"):
                current_p = st.session_state.provider_selector
                with st.spinner(f"AI ({current_p}) đang phân tích..."):
                    try:
                        loop = asyncio.get_event_loop()
                        # Gọi Orchestrator xử lý
                        response = loop.run_until_complete(
                            st.session_state.orchestrator.handle_request(prompt)
                        )
                        
                        # LẤY DANH SÁCH NGHIỆP VỤ TỪ SESSION STATE (Do Orchestrator lưu vào)
                        detected_tasks = st.session_state.get("last_tasks", [])
                        
                        # HIỂN THỊ NHÃN NGHIỆP VỤ NGAY LẬP TỨC
                        if detected_tasks:
                            tag_html = "".join([f'<span style="background-color: #e1f5fe; color: #01579b; padding: 2px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; margin-right: 5px; border: 1px solid #b3e5fc;">🔍 {t.upper()}</span>' for t in detected_tasks])
                            st.markdown(tag_html, unsafe_allow_html=True)
                        
                        st.markdown(response)
                        
                        # Lưu vào lịch sử kèm theo danh sách task để khi load lại vẫn thấy tag
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response,
                            "tasks": detected_tasks
                        })
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Lỗi: {str(e)}")



with log_col:
    st.subheader("📜 Nhật ký Database")
    log_placeholder = st.empty()
    db_path = "data/database/history.db"
    
    if os.path.exists(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                # 1. Kiểm tra xem bảng có cột 'task_names' chưa
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(chat_history)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # 2. Nếu là bảng cũ (task_name), ta tự động đổi tên cột hoặc dùng Alias
                query_col = "task_names" if "task_names" in columns else "task_name AS task_names"
                
                query = f"SELECT timestamp, {query_col}, user_query FROM chat_history ORDER BY id DESC LIMIT 15"
                df = pd.read_sql_query(query, conn)
                
                if not df.empty:
                    log_placeholder.dataframe(df, width='stretch', hide_index=True)
                else:
                    st.info("Chưa có cuộc hội thoại nào được lưu.")
        except Exception as e:
            # Hiện lỗi thật để anh em mình dễ bắt bệnh
            st.error(f"Lỗi truy xuất DB: {str(e)}")
    else:
        st.info("Đang chờ tạo file dữ liệu...")