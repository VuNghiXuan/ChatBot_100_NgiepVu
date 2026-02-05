import asyncio
import sqlite3
import threading
import os
import re # Thêm Regex để bóc tách mã
from datetime import datetime
import streamlit as st
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

    async def _call_llm(self, prompt):
        """Bọc hàm gọi LLM để xử lý cả Async và Sync linh hoạt"""
        if hasattr(self.llm, 'ainvoke'):
            res = await self.llm.ainvoke(prompt)
        elif hasattr(self.llm, 'invoke'):
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, self.llm.invoke, prompt)
        else:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, self.llm.chat, prompt)
        return res.content if hasattr(res, 'content') else res

    def _save_to_db_worker(self, task_names, query, response):
        try:
            db_full_path = os.path.abspath(self.db_path)
            conn = sqlite3.connect(db_full_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (timestamp, task_names, user_query, bot_response, provider)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  str(task_names), query, response, "System"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Lỗi ghi log ngầm: {e}")

    async def handle_request(self, query):
        # 1. PHÂN TÍCH Ý ĐỊNH (CẢI TIẾN VỚI REGEX)
        task_list_str = "\n".join([f"- {k}: {v}" for k, v in self.tasks_info.items()])
        
        intent_prompt = f"""
            BẠN LÀ ROBOT PHÂN LOẠI CỦA TIỆM VÀNG KIM PHÁT HIỆP THÀNH.
            Nhiệm vụ: Đọc câu hỏi và liệt kê các MÃ NGHIỆP VỤ liên quan nhất.

            DANH SÁCH MÃ:
            {task_list_str}

            QUY TẮC:
            - Nếu câu hỏi liên quan đến nhiều nghiệp vụ, hãy liệt kê TẤT CẢ các mã (ví dụ: gia_vang, quy_dinh_doi_tra, ke_toan).
            - CHỈ TRẢ VỀ CÁC MÃ, KHÔNG GIẢI THÍCH DÀI DÒNG.

            CÂU HỎI: "{query}"
            MÃ TRẢ VỀ:"""
        
        intent_res = await self._call_llm(intent_prompt)
        print(f"\n🔍 AI PHẢN HỒI (GỐC): {intent_res}") 

        # Dùng Regex để nhặt sạch các từ có trong phản hồi và so khớp với TaskRegistry
        potential_codes = re.findall(r'\w+', intent_res.lower())
        detected_tasks = [t for t in potential_codes if t in self.tasks_info]
        
        print(f"🎯 DANH SÁCH MÃ HỢP LỆ SAU LỌC: {detected_tasks}")

        st.session_state["last_tasks"] = detected_tasks if detected_tasks else ["tro_chuyen"]

        if not detected_tasks:
            # ÉP VAI NHÂN VIÊN KHI KHÔNG CÓ DỮ LIỆU
            final_prompt = f"""Bạn là nhân viên tiệm vàng Kim Phát Hiệp Thành. 
            Dữ liệu tiệm chưa có thông tin về: {query}. 
            Hãy xin lỗi và hướng dẫn khách hỏi về giá vàng, quy định hoặc đổi trả."""
            response = await self._call_llm(final_prompt)
        else:
            # 2. TRUY XUẤT DỮ LIỆU SONG SONG
            results = await asyncio.gather(*[
                self.connector.get_data_async(name, query) for name in detected_tasks
            ])
            
            full_context = "\n\n".join(results)
            instructions = [TaskRegistry.get_instruction(name) for name in detected_tasks]
            combined_instr = "\n".join([f"- {i}" for i in instructions])
            
            # 3. TỔNG HỢP PHẢN HỒI (VÒNG KIM CÔ)
            final_prompt = f"""
            BẠN LÀ NHÂN VIÊN TIỆM VÀNG KIM PHÁT HIỆP THÀNH.
            
            DỮ LIỆU THỰC TẾ:
            {full_context}

            QUY TẮC BẮT BUỘC:
            {combined_instr}
            - Tuyệt đối không tự chế số liệu.
            - Không dùng ví dụ iPhone/RMB.
            - Nếu khách hỏi liệt kê, hãy dùng bảng Markdown sạch đẹp, không có 'NaN' hay 'Unnamed'.

            CÂU HỎI: {query}
            TRẢ LỜI:"""
            
            response = await self._call_llm(final_prompt)

        # 4. GHI LOG NGẦM
        threading.Thread(
            target=self._save_to_db_worker, 
            args=(detected_tasks, query, response),
            daemon=True 
        ).start()

        return response