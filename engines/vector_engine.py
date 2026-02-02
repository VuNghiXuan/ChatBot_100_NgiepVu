"""1. File: engines/vector_engine.py
File này có nhiệm vụ: Chia nhỏ văn bản (PDF, Docx) -> Chuyển thành Vector -> Lưu vào bộ nhớ FAISS."""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

class VectorEngine:
    def __init__(self, data_path):
        self.data_path = data_path
        # Model embedding để hiểu tiếng Việt (chạy local)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.vector_db = None
        self._build_index()

    def _build_index(self):
        """Quét file trong thư mục và tạo kho lưu trữ vector"""
        documents = []
        if os.path.isfile(self.data_path):
            files = [self.data_path]
        else:
            files = [os.path.join(self.data_path, f) for f in os.listdir(self.data_path)]

        for file in files:
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file)
            elif file.endswith(".docx"):
                loader = Docx2txtLoader(file)
            else: continue
            documents.extend(loader.load())

        # Chia nhỏ văn bản để AI không bị "ngộp"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        # Tạo database vector
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)

    def retrieve(self, query: str):
        """Tìm kiếm nội dung liên quan nhất với câu hỏi"""
        if not self.vector_db: return "Không tìm thấy dữ liệu."
        
        # Lấy 3 đoạn văn bản có ý nghĩa gần nhất
        docs = self.vector_db.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        return context