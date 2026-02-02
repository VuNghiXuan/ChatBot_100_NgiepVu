"""2. File core/llm_factory.py (Nếu anh chưa viết nốt)
File này giúp main.py gọi AI một cách linh hoạt."""

from langchain_google_genai import ChatGoogleGenerativeAI

class LLMFactory:
    @staticmethod
    def get_model(model_type, api_key):
        if model_type == "Gemini":
            return LLMInstance(ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key))
        # Có thể thêm Groq hoặc Ollama ở đây
        raise ValueError("Model không được hỗ trợ")

class LLMInstance:
    def __init__(self, model):
        self.model = model

    def chat(self, prompt):
        response = self.model.invoke(prompt)
        return response.content