"""5. core/orchestrator.py (Bộ não điều phối)
Kết nối Router, Connector và LLM lại với nhau."""

from core.registry import TaskRegistry
from utils.router import SemanticRouter
from core.connector import SmartConnector
import sqlite3
from datetime import datetime

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.router = SemanticRouter(TaskRegistry.get_all_descriptions())
        self.connector = SmartConnector(TaskRegistry.TASKS)
        self.db_path = "data/database/history.db"
        self._init_db()

    def handle_request(self, query):
        # 1. Xác định nghiệp vụ
        task_name = self.router.route(query)
        
        if not task_name:
            return self.llm.chat("Xin lỗi, tôi chưa được huấn luyện cho nghiệp vụ này.")

        # 2. Lấy đúng "nhân viên" (Engine) cho nghiệp vụ đó
        engine = self.connector.get_engine(task_name)
        
        # 3. Truy xuất dữ liệu (Context)
        context = engine.retrieve(query)
        
        # 4. Để LLM trả lời dựa trên context
        prompt = f"Dựa trên dữ liệu sau: {context}\nCâu hỏi: {query}\nTrả lời ngắn gọn, chuyên nghiệp."
        return self.llm.chat(prompt)
    
    def _init_db(self):
        """Khởi tạo bảng lưu trữ nếu chưa có"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task_name TEXT,
                user_query TEXT,
                bot_response TEXT,
                provider TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_to_db(self, task_name, query, response):
        """Lưu nhật ký vào SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (timestamp, task_name, user_query, bot_response, provider)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
              task_name, query, response, self.llm.provider_name))
        conn.commit()
        conn.close()

    def handle_request(self, query):
        # 1. Định tuyến nghiệp vụ
        task_name = self.router.route(query) or "Unknown"
        
        # 2. Lấy dữ liệu và LLM trả lời (Logic cũ của anh)
        # ... (giả sử kết quả trả về là response)
        engine = self.connector.get_engine(task_name)
        context = engine.retrieve(query)
        prompt = f"Dữ liệu: {context}\nCâu hỏi: {query}"
        response = self.llm.chat(prompt)

        # 3. LƯU VÀO DATABASE
        self.save_to_db(task_name, query, response)

        return response
