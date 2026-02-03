class TaskRegistry:
    TASKS = {
        "gia_vang": {
        "description": "Tra cứu giá vàng hôm nay, tính toán tiền mua bán vàng.",
        "source_type": "FILE",
        "file_path": "data/database/gia_vang.xlsx",
        "instruction": """
            - Lấy giá vàng từ dữ liệu và nhân với số lượng khách hỏi.
            - KHÔNG trình bày dưới dạng công thức toán học (ví dụ: không dùng 2 x 76.500.000).
            - CHỈ ghi kết quả cuối cùng theo cách nói tự nhiên. 
            - Ví dụ: 'Dạ, 2 chỉ vàng 9999 của anh hết tổng cộng 153.000.000 VNĐ ạ.'
            - Định dạng số tiền có dấu chấm phân cách hàng nghìn.
        """
        },
        
        "ke_toan_hoa_don": {
            "description": "Quy tắc tính chênh lệch, tiền công và hướng dẫn xuất hóa đơn điện tử.",
            "source_type": "FILE",
            "file_path": "data/knowledge/logic_xuat_hd.json",
            "instruction": "Sử dụng công thức TLV_CL = Bán - Đổi. Trả lời đúng trọng tâm kế toán."
        },
        "bao_hanh": {
            "description": "Chính sách thu mua lại vàng, đổi trả trong 5 ngày, quy định về quà tặng, tặng hộp nhung khi mua vàng, yêu cầu giấy đảm bảo.",
            "source_type": "FILE",
            "file_path": "data/training/Quy_dinh_tiem_vang.docx",
            "instruction": "Trích xuất quy định thu hồi và quà tặng hộp nhung. Nhấn mạnh quy định 5 ngày và Giấy đảm bảo."
        }
    }

    @classmethod
    def get_all_descriptions(cls):
        return {name: info["description"] for name, info in cls.TASKS.items()}

    @classmethod
    def get_instruction(cls, task_name):
        return cls.TASKS.get(task_name, {}).get("instruction", "Trả lời lịch sự dựa trên dữ liệu.")