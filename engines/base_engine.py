"""
1. engines/base_engine.py (Lớp mẫu chung)
Mọi nhân viên (Engine) mới sau này đều phải tuân theo mẫu này.
"""

from abc import ABC, abstractmethod

class BaseEngine(ABC):
    @abstractmethod
    def retrieve(self, query: str):
        """Mọi Engine phải có hàm này để lấy dữ liệu"""
        pass