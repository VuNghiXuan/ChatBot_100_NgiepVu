"""2. core/connector.py (Bộ chuyển mạch thông minh)
File này giúp anh linh động giữa File, Database và API mà không cần sửa code ở các phần khác.
"""

import os
from engines.sql_engine import SQLEngine
from engines.api_engine import APIEngine

class SmartConnector:
    def __init__(self, config):
        self.config = config

    def get_engine(self, task_name):
        # Lấy cấu hình nguồn dữ liệu cho từng nghiệp vụ từ config/settings.yaml
        task_config = self.config.get(task_name, {})
        source_type = task_config.get("source_type", "FILE")

        if source_type == "DB":
            # Trả về Engine kết nối Database thật
            return SQLEngine(task_config.get("db_url"))
        elif source_type == "API":
            # Trả về Engine gọi API Backend
            return APIEngine(task_config.get("api_url"))
        else:
            # Mặc định dùng file local (Excel/CSV)
            return SQLEngine(task_config.get("file_path"))