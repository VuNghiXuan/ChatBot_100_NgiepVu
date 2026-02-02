"""5. core/orchestrator.py (Bộ não điều phối)
Kết nối Router, Connector và LLM lại với nhau."""

from core.registry import TaskRegistry
from utils.router import SemanticRouter
from core.connector import SmartConnector

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.router = SemanticRouter(TaskRegistry.get_all_descriptions())
        self.connector = SmartConnector(TaskRegistry.TASKS)

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