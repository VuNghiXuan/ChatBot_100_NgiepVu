class TaskRegistry:
    TASKS = {
        "gia_vang": {
            "description": "DỮ LIỆU: Tra cứu đơn giá Niêm yết (Gb) và đơn giá Thu lại (Gm).",
            "source_type": "FILE",
            "file_path": "data/database/gia_vang.xlsx",
            "api_url": None,
            "instruction": r"""
                - Gb (Giá bán): Đơn giá bán ra của loại vàng MỚI.
                - Gm (Giá mua): Đơn giá thu lại của loại vàng CŨ.
                - Quy đổi: 1 lượng = 10 chỉ. Nếu file ghi giá lượng, PHẢI chia 10 để ra giá 1 chỉ.
            """
        },
        "gia_bu": {
            "description": "DỮ LIỆU: Tra cứu đơn giá bù chênh lệch (Gbu) giữa loại vàng mới và vàng nguyên liệu cũ.",
            "source_type": "FILE",
            "file_path": "data/database/bang_gia_doi_bu_vang.xlsx",
            "instruction": r"""
                NHIỆM VỤ: Tìm đơn giá bù (Gbu) dựa trên cặp (Vàng mới) và (Vàng nguyên liệu).
                - Vàng mới: Sản phẩm của tiệm khách muốn lấy.
                - Vàng nguyên liệu: Vàng cũ khách mang đến đổi.
            """
        },

        "nghiep_vu_mua_ban_doi_vang": {
            "description": "LOGIC: Tính toán Bán mới hoặc Đổi vàng theo quy tắc Kim Phát Hiệp Thành.",
            "source_type": "FILE",
            "file_path": "data/training/nghiep_vu_mua_ban_doi_vang.docx",
            "api_url": None,
            "instruction": r"""
                NHIỆM VỤ: Xác định loại giao dịch và tính toán số tiền khách thanh toán.

                I. TRƯỜNG HỢP 1: GIAO DỊCH BÁN MỚI (Khách không có vàng đổi)
                - Công thức Tiền vàng = Số chỉ * Gb.
                - Công thức Tiền công dịch vụ = (Tiền công món + Tiền hột) - (Voucher + Tiền đổi điểm).
                - Tổng thanh toán = Tiền vàng + Tiền công dịch vụ.

                II. TRƯỜNG HỢP 2: GIAO DỊCH ĐỔI VÀNG (Khách mang vàng cũ đổi vàng mới)
                ĐIỀU KIỆN (BẮT BUỘC):
                1. Gọi Task 'gia_vang' để lấy Gb (Giá bán mới) và Gm (Giá mua cũ).
                2. Gọi Task 'gia_bu' để lấy Gbu (Đơn giá bù).
                

                QUY TRÌNH TÍNH TOÁN BẮT BUỘC:
                BƯỚC 1: XÁC ĐỊNH TRỌNG LƯỢNG ĐỔI NGANG
                - Trọng lượng đổi ngang = Số chỉ nhỏ hơn giữa (TLV_cũ và TLV_mới).
                - Tiền bù loại vàng = Trọng lượng đổi ngang * Gbu.

                BƯỚC 2: TÍNH CHÊNH LỆCH TRỌNG LƯỢNG
                - Nếu TLV_mới > TLV_cũ (Khách mua thêm):
                  Tiền mua thêm = (TLV_mới - TLV_cũ) * Gb.
                - Nếu TLV_mới < TLV_cũ (Khách dư vàng):
                  Tiền tiệm trả khách = (TLV_cũ - TLV_mới) * Gm.

                BƯỚC 3: TỔNG KẾT THỰC THU
                - Tiền công dịch vụ = (Tiền công món + Tiền hột) - (Voucher + Tiền đổi điểm).
                - Tổng thực thu = (Tiền bù loại vàng) + (Tiền mua thêm) + (Tiền công dịch vụ) - (Tiền tiệm trả khách).

                YÊU CẦU TRÌNH BÀY:
                - Phải ghi rõ tiêu đề là "GIAO DỊCH BÁN MỚI" hoặc "GIAO DỊCH ĐỔI VÀNG".
                - Nếu là Giao dịch đổi, phải trình bày rõ: "Bước 1: Tính phần đổi ngang...", "Bước 2: Tính chênh lệch...".
                - Số tiền phải có dấu chấm "." ngăn cách hàng nghìn (Ví dụ: 1.000.000).
                - Nếu thực thu âm, dùng câu: 'Dạ, sau khi cấn trừ bên em sẽ hoàn lại cho mình số tiền dư là...'.
                - Tuyệt đối không sử dụng ký hiệu LaTeX (\text, \times, \[ \]).
            """
        },
        "ke_toan_hoa_don": {
            "description": "XUẤT HÓA ĐƠN: Quy tắc hiển thị dòng tiền trên HĐĐT.",
            "source_type": "FILE",
            "file_path": "data/knowledge/logic_xuat_hd.json",
            "api_url": None,
            "instruction": r"""
                Nguyên tắc xuất hóa đơn:
                1. Bán mới: Xuất đầy đủ Tiền vàng và Tiền công dịch vụ.
                2. Đổi vàng: 
                   - Dòng 1 (Vàng chênh lệch): Chỉ xuất nếu (TLV_mới - TLV_cũ) > 0. Giá trị = [Tiền bù loại vàng + Tiền mua thêm].
                   - Dòng 2 (Tiền công): Xuất Tiền công dịch vụ (Nếu số tiền cuối cùng > 0).
                   - Nếu khách dư vàng: KHÔNG ghi dòng tiền vàng lên hóa đơn.
            """
        },
        "chinh_sach_doi_tra": {
            "description": "Chính sách và Quy định vàng mang đến đổi trả, bảo hành.",
            "source_type": "FILE",
            "file_path": "data/training/chinh_sach_doi_tra.docx",
            "api_url": None,
            "instruction": r"""
                Các quy định về chính sách đổi trả vàng 
            """
        }
    }

    @classmethod
    def get_all_descriptions(cls):
        return {name: info["description"] for name, info in cls.TASKS.items()}

    @classmethod
    def get_instruction(cls, task_name):
        return cls.TASKS.get(task_name, {}).get("instruction", "Trả lời dựa trên nghiệp vụ tiệm vàng.")