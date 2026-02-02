"""2. File core/llm_factory.py (Nếu anh chưa viết nốt)
File này giúp main.py gọi AI một cách linh hoạt."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama # Sử dụng bản mới từ langchain_ollama
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:
    @staticmethod
    def get_model(provider: str):
        """
        Lấy model dựa trên nhà cung cấp (Gemini, Groq, Ollama)
        """
        provider = provider.upper()

        if provider == "GEMINI":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Lỗi: Thiếu GOOGLE_API_KEY trong file .env")
            model = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
                google_api_key=api_key,
                temperature=0.3
            )
            # QUAN TRỌNG: Truyền thêm 'provider' vào LLMInstance
            return LLMInstance(model, provider)

        elif provider == "GROQ":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Lỗi: Thiếu GROQ_API_KEY trong file .env")
            model = ChatGroq(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), 
                groq_api_key=api_key,
                temperature=0.3
            )
            return LLMInstance(model, provider)

        elif provider == "OLLAMA":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
            model = ChatOllama(
                base_url=base_url,
                model=model_name,
                temperature=0.3
            )
            return LLMInstance(model, provider)

        raise ValueError(f"Nhà cung cấp {provider} chưa được hỗ trợ!")

class LLMInstance:
    def __init__(self, model, provider_name):
        """Lớp bọc thống nhất cách gọi hàm chat"""
        self.model = model
        self.provider_name = provider_name # Fix lỗi: Đã nhận tham số provider_name

    def chat(self, prompt: str):
        """Hàm chat đồng bộ"""
        response = self.model.invoke(prompt)
        return response.content
    
    async def chat_async(self, prompt: str):
        """Hàm chat bất đồng bộ (Dùng cho Orchestrator Async)"""
        response = await self.model.ainvoke(prompt)
        return response.content