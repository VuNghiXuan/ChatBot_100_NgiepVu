import asyncio
import sqlite3
import threading
import os
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

    # ĐÃ ĐỔI TÊN TỪ _safe_ainvoke THÀNH _call_llm ĐỂ KHỚP VỚI BÊN DƯỚI
    async def _call_llm(self, prompt):
        """Bọc hàm gọi LLM để xử lý cả Async và Sync linh hoạt"""
        if hasattr(self.llm, 'ainvoke'):
            res = await self.llm.ainvoke(prompt)
        elif hasattr(self.llm, 'invoke'):
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, self.llm.invoke, prompt)
        else:
            # Nếu class LLMInstance dùng hàm 'chat'
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, self.llm.chat, prompt)
            
        # Trích xuất nội dung nếu kết quả là object LangChain
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
        # 1. PHÂN TÍCH Ý ĐỊNH
        task_list_str = "\n".join([f"- {k}: {v}" for k, v in self.tasks_info.items()])
        
        intent_prompt = f"""
        BẠN LÀ CHUYÊN GIA ĐIỀU PHỐI TẠI TIỆM VÀNG VŨ NGHI XUÂN.
        Chọn TẤT CẢ các mã nghiệp vụ liên quan.
        
        NGHIỆP VỤ:
        {task_list_str}
        
        CÂU HỎI: "{query}"
        
        TRẢ VỀ: Chỉ ghi các mã, cách nhau dấu phẩy (Ví dụ: gia_vang, bao_hanh).
        MÃ CỦA BẠN:"""
        
        # Gọi qua hàm đã đồng bộ tên
        intent_res = await self._call_llm(intent_prompt)
        
        print(f"\n🔍 AI PHÂN LOẠI ĐƯỢC: {intent_res}") 
        
        detected_tasks = [t.strip().lower() for t in intent_res.split(",") 
                          if t.strip().lower() in self.tasks_info]
        
        print(f"🎯 DANH SÁCH MÃ HỢP LỆ: {detected_tasks}")

        st.session_state["last_tasks"] = detected_tasks if detected_tasks else ["tro_chuyen"]

        if not detected_tasks:
            response = await self._call_llm(f"Chào khách niềm nở: {query}")
        else:
            # 2. TRUY XUẤT DỮ LIỆU SONG SONG
            results = await asyncio.gather(*[
                self.connector.get_data_async(name, query) for name in detected_tasks
            ])
            
            for i, res in enumerate(results):
                print(f"📂 DỮ LIỆU TỪ TASK [{detected_tasks[i]}]: {res[:200]}...")

            instructions = [TaskRegistry.get_instruction(name) for name in detected_tasks]
            full_context = "\n\n".join(results)
            combined_instr = "\n".join([f"- {i}" for i in instructions])
            
            final_prompt = f"DỮ LIỆU: {full_context}\nQUY TẮC: {combined_instr}\nHỎI: {query}\nTRẢ LỜI:"
            response = await self._call_llm(final_prompt)

        # 3. GHI LOG NGẦM (Sử dụng Thread để không làm chậm UI)
        threading.Thread(
            target=self._save_to_db_worker, 
            args=(detected_tasks, query, response),
            daemon=True 
        ).start()

        return response