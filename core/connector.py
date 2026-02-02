"""2. core/connector.py (Bộ chuyển mạch thông minh)
File này giúp anh linh động giữa File, Database và API mà không cần sửa code ở các phần khác.
"""

import os
from engines.sql_engine import SQLEngine
from engines.api_engine import APIEngine
from engines.vector_engine import VectorEngine # Import thêm engine mới

class SmartConnector:
    def __init__(self, config):
        """
        config: Lấy từ TaskRegistry.TASKS
        """
        self.config = config

    def get_engine(self, task_name):
        # 1. Lấy cấu hình nguồn dữ liệu cho nghiệp vụ cụ thể
        task_config = self.config.get(task_name, {})
        source_type = task_config.get("source_type", "FILE")
        
        # 2. Bộ chuyển mạch (Switching Logic)
        if source_type == "DB":
            # Engine xử lý SQL Database (MySQL, Postgres, SQLite)
            return SQLEngine(task_config.get("db_url"))
            
        elif source_type == "API":
            # Engine xử lý gọi API bên ngoài hoặc nội bộ
            return APIEngine(task_config.get("api_url"))
            
        elif source_type == "VECTOR":
            # Engine xử lý Vector Database (Tra cứu PDF, Docx, Tài liệu chính sách)
            return VectorEngine(task_config.get("file_path"))
            
        else:
            # Mặc định: Xử lý các file cấu trúc như Excel, CSV
            return SQLEngine(task_config.get("file_path"))