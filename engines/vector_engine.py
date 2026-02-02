import os
import asyncio
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

class VectorEngine:
    def __init__(self, data_path):
        self.data_path = data_path
        # Model embedding đa ngôn ngữ (rất tốt cho tiếng Việt)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vector_db = None
        self._build_index()

    def _build_index(self):
        """Quét file và tạo kho lưu trữ vector"""
        documents = []
        
        # Kiểm tra đường dẫn tồn tại
        if not os.path.exists(self.data_path):
            print(f"Cảnh báo: Đường dẫn {self.data_path} không tồn tại.")
            return

        if os.path.isfile(self.data_path):
            files = [self.data_path]
        else:
            files = [os.path.join(self.data_path, f) for f in os.listdir(self.data_path) 
                     if f.endswith((".pdf", ".docx"))]

        if not files:
            print("Không tìm thấy file PDF hoặc DOCX để index.")
            return

        for file in files:
            try:
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file)
                elif file.endswith(".docx"):
                    loader = Docx2txtLoader(file)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Lỗi khi đọc file {file}: {e}")

        if documents:
            # Chia nhỏ văn bản (Chunking)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)
            
            # Tạo hoặc cập nhật database vector
            self.vector_db = FAISS.from_documents(chunks, self.embeddings)
            print(f"✅ Đã index {len(chunks)} đoạn văn bản từ {len(files)} file.")

    def retrieve(self, query: str):
        """Tìm kiếm nội dung (Đồng bộ)"""
        if not self.vector_db: 
            return "Không có dữ liệu tài liệu để tra cứu."
        
        docs = self.vector_db.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])

    async def aretrieve(self, query: str):
        """Tìm kiếm nội dung (Bất đồng bộ - Dùng cho Orchestrator Async)"""
        # FAISS similarity_search chạy trên CPU khá nhanh nên ta bọc trong loop.run_in_executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.retrieve, query)