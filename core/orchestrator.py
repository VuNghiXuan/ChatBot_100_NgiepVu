"""5. core/orchestrator.py (Bộ não điều phối)
Kết nối Router, Connector và LLM lại với nhau."""

import asyncio
import sqlite3
import threading
from datetime import datetime
from core.registry import TaskRegistry
from utils.router import SemanticRouter
from core.connector import SmartConnector

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        # Tải danh mục nghiệp vụ và cấu hình router
        self.router = SemanticRouter(TaskRegistry.get_all_descriptions())
        self.connector = SmartConnector(TaskRegistry.TASKS)
        
        # Cấu hình Database
        self.db_path = "data/database/history.db"
        self._init_db()

    def _init_db(self):
        """Khởi tạo bảng lưu trữ nếu chưa có (Chạy đồng bộ khi bắt đầu)"""
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

    def _save_to_db_worker(self, task_name, query, response, provider):
        """Hàm thực thi ghi DB chạy trong thread riêng để không gây trễ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (timestamp, task_name, user_query, bot_response, provider)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  task_name, query, response, provider))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Lỗi ghi log Database: {e}")

    async def handle_request(self, query):
        """Hành trình xử lý câu hỏi bất đồng bộ"""
        
        # 1. Xác định nghiệp vụ (Dùng Router)
        # Chạy trong thread pool nếu Router nặng, hoặc gọi trực tiếp nếu nhanh
        task_name = self.router.route(query) or "Chưa phân loại"
        
        if task_name == "Chưa phân loại":
            response = "Xin lỗi, tôi chưa được huấn luyện để xử lý yêu cầu này của anh/chị."
        else:
            # 2. Kết nối Engine và Truy xuất dữ liệu (Retrieval)
            engine = self.connector.get_engine(task_name)
            
            # Chạy truy xuất dữ liệu (Có thể dùng await nếu engine là async)
            context = engine.retrieve(query)
            
            # 3. Gửi prompt cho LLM xử lý (Phần tốn thời gian nhất)
            prompt = (
                f"Bạn là trợ lý ảo tiệm vàng chuyên nghiệp.\n"
                f"Dữ liệu nghiệp vụ: {context}\n"
                f"Câu hỏi khách hàng: {query}\n"
                f"Hãy trả lời ngắn gọn, chính xác dựa trên dữ liệu cung cấp."
            )
            
            # Giả sử hàm chat của LLM đã được nâng cấp lên async
            response = await self.llm.chat_async(prompt)

        # 4. Ghi log vào Database (Chạy ngầm bằng Threading để trả kết quả ngay cho khách)
        threading.Thread(
            target=self._save_to_db_worker, 
            args=(task_name, query, response, self.llm.provider_name)
        ).start()

        return response