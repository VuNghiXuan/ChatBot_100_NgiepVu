"""4. utils/router.py (Định tuyến thông minh)
File này dùng AI để chọn đúng nghiệp vụ trong 100 cái."""

from sentence_transformers import SentenceTransformer, util
import torch

class SemanticRouter:
    def __init__(self, task_descriptions):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.task_names = list(task_descriptions.keys())
        self.task_vecs = self.model.encode(list(task_descriptions.values()), convert_to_tensor=True)

    def route(self, user_query: str):
        query_vec = self.model.encode(user_query, convert_to_tensor=True)
        # Tính toán độ tương đồng giữa câu hỏi và 100 mô tả nghiệp vụ
        scores = util.cos_sim(query_vec, self.task_vecs)[0]
        best_idx = torch.argmax(scores).item()
        
        # Nếu độ tương đồng quá thấp, có thể coi là không thuộc nghiệp vụ nào
        if scores[best_idx] < 0.3:
            return None
            
        return self.task_names[best_idx]