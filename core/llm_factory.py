"""2. File core/llm_factory.py (Nếu anh chưa viết nốt)
File này giúp main.py gọi AI một cách linh hoạt."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:
    @staticmethod
    def get_model(provider: str):
        """
        Lấy model dựa trên nhà cung cấp (Gemini, Groq, Ollama)
        Cấu hình được lấy trực tiếp từ file .env
        """
        provider = provider.upper()

        if provider == "GEMINI":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Lỗi: Thiếu GOOGLE_API_KEY trong file .env")
            return LLMInstance(ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                google_api_key=api_key,
                temperature=0.3
            ))

        elif provider == "GROQ":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Lỗi: Thiếu GROQ_API_KEY trong file .env")
            return LLMInstance(ChatGroq(
                model="llama3-70b-8192", 
                groq_api_key=api_key,
                temperature=0.3
            ))

        elif provider == "OLLAMA":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = os.getenv("OLLAMA_MODEL", "llama3")
            return LLMInstance(ChatOllama(
                base_url=base_url,
                model=model_name,
                temperature=0.3
            ))

        raise ValueError(f"Nhà cung cấp {provider} chưa được hỗ trợ!")

class LLMInstance:
    def __init__(self, model, provider_name):
        """Lớp bọc để thống nhất cách gọi hàm chat giữa các nhà cung cấp"""

        self.model = model
        self.provider_name = provider_name # Lưu tên để biết câu này do AI nào trả lời

    def chat(self, prompt: str):
        response = self.model.invoke(prompt)
        # LangChain trả về kết quả trong trường .content
        return response.content