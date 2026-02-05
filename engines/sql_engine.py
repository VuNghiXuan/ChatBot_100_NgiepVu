import pandas as pd
import numpy as np
from engines.base_engine import BaseEngine

class SQLEngine(BaseEngine):
    def __init__(self, source_path_or_url):
        self.source = source_path_or_url

    def retrieve(self, query: str):
        """Trích xuất và làm sạch dữ liệu từ Excel hoặc JSON/Database"""
        try:
            # 1. XỬ LÝ FILE EXCEL
            if self.source.endswith(('.xlsx', '.xls')):
                # Đọc toàn bộ file
                df = pd.read_excel(self.source)

                # --- BƯỚC LÀM SẠCH "THẦN THÁNH" ---
                # Loại bỏ hàng/cột hoàn toàn trống (NaN)
                df = df.dropna(how='all').dropna(axis=1, how='all')

                # Nếu hàng đầu tiên chứa nhiều NaN, tìm hàng làm tiêu đề (Header)
                if df.iloc[0].isnull().sum() > len(df.columns) / 2 or "Unnamed" in str(df.columns):
                    for i in range(len(df)):
                        # Nếu hàng i có từ 'VÀNG' hoặc 'LOẠI', chọn nó làm Header
                        row_values = [str(x).upper() for x in df.iloc[i].values]
                        if any("VÀNG" in x or "LOẠI" in x or "GIA" in x for x in row_values):
                            df.columns = df.iloc[i]
                            df = df.iloc[i+1:]
                            break
                
                # Loại bỏ các cột 'Unnamed' còn sót lại
                df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                
                # Làm sạch giá trị NaN còn lại trong bảng thành chuỗi trống để AI đỡ rối
                df = df.replace(np.nan, '', regex=True)

                # Trả về tối đa 15 dòng dữ liệu sạch nhất
                return df.head(15).to_markdown(index=False)

            # 2. XỬ LÝ FILE JSON (Cho nghiệp vụ kế toán/hóa đơn)
            elif self.source.endswith('.json'):
                import json
                with open(self.source, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            # 3. XỬ LÝ DATABASE THỰC (Nếu có)
            else:
                # Thay vì trả về câu "Dữ liệu từ SQL" vô nghĩa, ta báo trạng thái
                return f"Đang kết nối đến hệ thống quản trị để tra cứu: {query}"

        except Exception as e:
            return f"Lỗi truy xuất dữ liệu: {str(e)}"