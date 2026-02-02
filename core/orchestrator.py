"""5. core/orchestrator.py (Bộ não điều phối)
Kết nối Router, Connector và LLM lại với nhau."""

import asyncio
import sqlite3
import threading
import streamlit as st # Thêm để lưu trạng thái giao diện
from datetime import datetime
from core.registry import TaskRegistry
from core.connector import SmartConnector

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.connector = SmartConnector(TaskRegistry.TASKS)
        self.tasks_info = TaskRegistry.get_all_descriptions()
        
        self.db_path = "data/database/history.db"
        self._init_db()

    def _init_db(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task_names TEXT,
                user_query TEXT,
                bot_response TEXT,
                provider TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _save_to_db_worker(self, task_names, query, response, provider):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (timestamp, task_names, user_query, bot_response, provider)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  task_names, query, response, provider))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Lỗi ghi log Database: {e}")

    async def handle_request(self, query):
        # 1. PHÂN TÍCH Ý ĐỊNH (ÉP BUỘC)
        task_list_str = "\n".join([f"- {k}: {v}" for k, v in self.tasks_info.items()])
        
        intent_prompt = f"""
        BẠN LÀ CHUYÊN VIÊN PHÂN LOẠI CỦA TIỆM VÀNG.
        Nhiệm vụ: Đọc câu hỏi và trả về MÃ NGHIỆP VỤ phù hợp từ danh sách bên dưới.

        DANH SÁCH:
        {task_list_str}

        VÍ DỤ:
        - Khách hỏi: "Giá vàng hôm nay" -> Trả về: gia_vang
        - Khách hỏi: "18k bao nhiêu" -> Trả về: gia_vang
        - Khách hỏi: "Vàng 9999 bao nhiêu một chỉ" -> Trả về: gia_vang

        QUY TẮC: 
        - CHỈ TRẢ VỀ MÃ, KHÔNG GIẢI THÍCH. 
        - Nếu câu hỏi liên quan đến tiền bạc, giá cả vàng -> BẮT BUỘC trả về 'gia_vang'.
        - Nếu không có cái nào khớp -> Trả về 'none'.

        CÂU HỎI CỦA KHÁCH: "{query}"
        MÃ TRẢ VỀ:"""

        detected_tasks_raw = await self.llm.chat_async(intent_prompt)
        # Làm sạch chuỗi trả về
        detected_tasks = [t.strip().lower() for t in detected_tasks_raw.split(",") if t.strip().lower() in self.tasks_info]

        st.session_state["last_tasks"] = detected_tasks if detected_tasks else ["tro_chuyen"]

        if not detected_tasks:
            # Nếu AI vẫn không chịu chọn task, ta ép nó trả lời theo vai nhân viên
            final_prompt = f"Bạn là nhân viên tiệm vàng, hãy trả lời câu hỏi sau một cách niềm nở: {query}"
            response = await self.llm.chat_async(final_prompt)
        else:
            # 2. TRUY XUẤT DỮ LIỆU
            all_contexts = []
            async def fetch_data(t_name):
                engine = self.connector.get_engine(t_name)
                data = await engine.aretrieve(query) if hasattr(engine, 'aretrieve') else engine.retrieve(query)
                return f"--- DỮ LIỆU THỰC TẾ {t_name.upper()} ---\n{data}"

            results = await asyncio.gather(*[fetch_data(name) for name in detected_tasks])
            full_context = "\n\n".join(results)
            
            # 3. ÉP AI TRẢ LỜI DỰA TRÊN DỮ LIỆU
            final_prompt = f"""
            BẠN LÀ NHÂN VIÊN TIỆM VÀNG ĐANG TRỰC CHAT.
            Dưới đây là dữ liệu thực tế tại cửa hàng:
            {full_context}

            CÂU HỎI CỦA KHÁCH: {query}

            YÊU CẦU:
            1. Dựa hoàn toàn vào 'DỮ LIỆU THỰC TẾ' để trả lời. 
            2. Tuyệt đối KHÔNG ĐƯỢC nói 'tôi không biết' hay 'tôi không truy cập được dữ liệu'. 
            3. Nếu khách hỏi giá, hãy lấy con số trong dữ liệu cung cấp và trình bày rõ ràng.
            4. Trình bày bằng Markdown, có tiêu đề ### rõ ràng.
            """
            response = await self.llm.chat_async(final_prompt)
            
        return response