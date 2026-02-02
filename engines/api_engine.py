# Các nghiệp vụ gọi API sau này (ví dụ tra cứu tỷ giá vàng từ server bên ngoài)

import requests
import asyncio

class APIEngine:
    def __init__(self, api_url):
        self.api_url = api_url

    def retrieve(self, query: str):
        """
        Hàm lấy dữ liệu từ API bên ngoài.
        Tạm thời trả về thông báo nếu chưa cấu hình URL thật.
        """
        if not self.api_url:
            return "Lỗi: Chưa cung cấp API URL cho nghiệp vụ này."
        
        try:
            # Ví dụ: Gọi API lấy dữ liệu
            # response = requests.get(f"{self.api_url}?q={query}", timeout=10)
            # return response.json()
            return f"Dữ liệu mẫu từ API tại địa chỉ: {self.api_url}"
        except Exception as e:
            return f"Lỗi kết nối API: {str(e)}"

    async def retrieve_async(self, query: str):
        """Phiên bản chạy bất đồng bộ cho Orchestrator mới"""
        return self.retrieve(query)