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
st.set_page_config(page_title="AI Tiệm Vàng - Vũ Nghi Xuân", layout="wide", page_icon="💎")

# --- HÀM KHỞI TẠO HỆ THỐNG (ĐÃ TỐI ƯU) ---
def init_system(provider):
    """Khởi tạo toàn bộ não bộ và công cụ điều phối"""
    try:
        # Xóa cache cũ nếu có để đảm bảo nạp lại file mới (Excel, Word)
        st.cache_resource.clear() 
        
        # 1. Lấy model AI từ Factory
        llm = LLMFactory.get_model(provider)
        
        # 2. Khởi tạo Orchestrator 
        # (Nó sẽ tự gọi SmartConnector và nạp lại Engines bên trong)
        return Orchestrator(llm) 
        
    except Exception as e:
        st.error(f"❌ Lỗi khởi tạo hệ thống: {str(e)}")
        return None

# --- XỬ LÝ SỰ KIỆN ---
def on_provider_change():
    st.session_state.orchestrator = init_system(st.session_state.provider_selector)

# --- KHỞI TẠO SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "orchestrator" not in st.session_state:
    # Mặc định lấy Ollama hoặc cái đầu tiên trong danh sách
    st.session_state.orchestrator = init_system("Ollama")

# --- GIAO DIỆN SIDEBAR ---
with st.sidebar:
    st.header("💎 Vũ Nghi Xuân Admin")
    
    options = ["Ollama", "Gemini", "Groq"]
    st.selectbox(
        "Chọn não bộ AI:",
        options=options,
        index=0,
        key="provider_selector",
        on_change=on_provider_change
    )
    
    st.divider()
    
    # NÚT LÀM MỚI (CẬP NHẬT)
    if st.button("🔄 Làm mới dữ liệu (Re-index)", width="stretch"):
        with st.spinner("Đang xóa bộ nhớ đệm và nạp lại dữ liệu..."):
            # 1. Xóa bộ nhớ đệm của Connector (nếu có)
            if hasattr(st.session_state.orchestrator.connector, 'clear_cache'):
                st.session_state.orchestrator.connector.clear_cache()
                
            # 2. Khởi tạo lại toàn bộ hệ thống
            st.session_state.orchestrator = init_system(st.session_state.provider_selector)
            
            st.success("✅ Đã cập nhật giá vàng & chính sách mới từ file!")
            st.rerun()

    if st.button("🗑 Xóa lịch sử Chat", width="stretch"):
        st.session_state.messages = []
        st.rerun()

# --- LAYOUT CHÍNH ---
st.title("🤖 Trợ Lý AI Tiệm Vàng Đa Nghiệp Vụ")
st.markdown("---")

chat_col, log_col = st.columns([2, 1])

with chat_col:
    st.subheader("💬 Trò chuyện trực tuyến")
    
    chat_container = st.container(height=550) 
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "tasks" in message:
                    # Hiển thị nhãn nghiệp vụ (Tag)
                    tags = "".join([f'<span style="background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; margin-right: 5px; border: 1px solid #ffcc80;">⚙️ {t.upper()}</span>' for t in message["tasks"]])
                    st.markdown(tags, unsafe_allow_html=True)
                st.markdown(message["content"])

    # Xử lý tin nhắn mới
    if prompt := st.chat_input("Hãy đặt câu hỏi về nghiệp vụ vàng trang sức?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                current_p = st.session_state.provider_selector
                with st.spinner(f"Đang tra cứu hệ thống ({current_p})..."):
                    try:
                        # Gọi Orchestrator bằng Async
                        loop = asyncio.get_event_loop()
                        response = loop.run_until_complete(
                            st.session_state.orchestrator.handle_request(prompt)
                        )
                        
                        detected_tasks = st.session_state.get("last_tasks", [])
                        
                        if detected_tasks:
                            tags = "".join([f'<span style="background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; margin-right: 5px; border: 1px solid #ffcc80;">⚙️ {t.upper()}</span>' for t in detected_tasks])
                            st.markdown(tags, unsafe_allow_html=True)
                        
                        st.markdown(response)
                        
                        # Lưu vào lịch sử
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response,
                            "tasks": detected_tasks
                        })
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Lỗi xử lý: {str(e)}")

# --- CỘT NHẬT KÝ DATABASE ---
with log_col:
    st.subheader("📜 Nhật ký hệ thống")
    db_path = "data/database/history.db"
    
    if os.path.exists(db_path):
        try:
            # Dùng context manager để tránh treo file SQLite
            with sqlite3.connect(db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT timestamp as 'Thời gian', 
                           task_names as 'Nghiệp vụ', 
                           user_query as 'Câu hỏi' 
                    FROM chat_history 
                    ORDER BY id DESC LIMIT 15
                """, conn)
                
                if not df.empty:
                    st.dataframe(df, width="stretch", hide_index=True)
                else:
                    st.info("Chưa có dữ liệu hội thoại.")
        except Exception as e:
            st.info("Đang chờ dữ liệu mới...")
    else:
        st.info("Hệ thống nhật ký đang khởi tạo...")