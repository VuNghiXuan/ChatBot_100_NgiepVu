"""3. core/registry.py (Danh mục 100+ Nghiệp vụ)
Nơi anh khai báo danh sách "nhân viên" và mô tả công việc của họ."""

class TaskRegistry:
    # Sau này anh thêm 100 nghiệp vụ vào đây chỉ bằng cách thêm dòng
    TASKS = {
        "gia_vang": {
            "description": "Tra cứu giá vàng hôm nay, giá mua vào bán ra, giá đổi các loại vàng.",
            "source_type": "FILE",
            "file_path": "data/database/gia_vang.xlsx"
        },
        "cam_do": {
            "description": "Quy định về lãi suất cầm đồ, thời hạn thanh lý và thủ tục.",
            "source_type": "API",
            "api_url": "https://api.tiemvang.com/pawn-policy"
        },
        "bao_hanh": {
            "description": "Chính sách bảo hành, đánh bóng, sửa chữa sản phẩm, chính sách mua bán, đổi trả.",
            "source_type": "FILE",
            "file_path": "data/training/Quy_dinh_tiem_vang.docx"
        }
    }

    @classmethod
    def get_all_descriptions(cls):
        return {name: info["description"] for name, info in cls.TASKS.items()}