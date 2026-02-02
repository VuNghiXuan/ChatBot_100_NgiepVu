import pandas as pd
from engines.base_engine import BaseEngine

class SQLEngine(BaseEngine):
    def __init__(self, source_path_or_url):
        self.source = source_path_or_url

    def retrieve(self, query: str):
        """Trích xuất dữ liệu từ Excel hoặc Database"""
        try:
            # Nếu là file Excel cục bộ
            if self.source.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.source)
                # Logic đơn giản: Trả về 5 dòng đầu hoặc kết quả lọc
                return df.head(10).to_string()
            
            # Nếu là Database URL (SQLAlchemy)
            else:
                # Code tra cứu SQL tại đây
                return "Dữ liệu từ Database SQL"
        except Exception as e:
            return f"Lỗi truy xuất dữ liệu: {str(e)}"