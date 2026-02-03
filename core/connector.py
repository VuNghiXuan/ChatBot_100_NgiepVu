"""2. core/connector.py (Bộ chuyển mạch thông minh)
File này giúp anh linh động giữa File, Database và API mà không cần sửa code ở các phần khác.
"""

# core/connector.py
from engines.sql_engine import SQLEngine
from engines.vector_engine import VectorEngine
from core.registry import TaskRegistry

class SmartConnector:
    def __init__(self, config):
        # config ở đây chính là TaskRegistry.TASKS
        self.config = config
        # Dùng cache để mỗi Engine (Excel hay Vector) chỉ khởi tạo 1 lần duy nhất
        self._engine_cache = {}

    def get_engine(self, task_name):
        # 1. Nếu engine này đã có trong kho rồi thì bốc ra dùng luôn
        if task_name in self._engine_cache:
            return self._engine_cache[task_name]

        # 2. Nếu chưa có, bắt đầu đọc cấu hình từ Registry
        task_config = self.config.get(task_name, {})
        source_type = task_config.get("source_type", "FILE")
        path = task_config.get("file_path")

        # 3. Khởi tạo Engine tương ứng
        if source_type == "DB" or (source_type == "FILE" and path.endswith(('.xlsx', '.xls'))):
            engine = SQLEngine(path)
        elif source_type == "VECTOR":
            engine = VectorEngine(path)
        else:
            engine = SQLEngine(path) # Mặc định

        # Lưu vào cache để lần sau khách hỏi không phải load lại file nữa
        self._engine_cache[task_name] = engine
        return engine

    def get_data(self, task_name, query):
        """Hàm này để Orchestrator gọi lấy dữ liệu"""
        engine = self.get_engine(task_name)
        return engine.retrieve(query)

    async def get_data_async(self, task_name, query):
        """Hàm này để Orchestrator gọi kiểu bất đồng bộ"""
        engine = self.get_engine(task_name)
        # Nếu là VectorEngine thì dùng aretrieve cho nhanh, còn lại dùng retrieve
        if hasattr(engine, 'aretrieve'):
            return await engine.aretrieve(query)
        return engine.retrieve(query)