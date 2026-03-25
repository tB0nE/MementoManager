import os
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "models/mistral-7b-v0.3.Q4_K_M.gguf")
        if not os.path.isabs(self.model_path):
            self.model_path = os.path.abspath(os.path.join(os.getcwd(), self.model_path))
        self.n_gpu_layers = int(os.getenv("N_GPU_LAYERS", "-1"))
        self._model = None

    @property
    def model(self):
        if self._model is None:
            if not os.path.exists(self.model_path):
                print(f"Warning: Model not found at {self.model_path}.")
                return None
            self._model = Llama(
                model_path=self.model_path,
                n_gpu_layers=-1, # Force all layers to GPU
                n_ctx=8192,
                verbose=False
            )
        return self._model

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        model = self.model
        if not model:
            return "Error: Model not loaded."
        
        response = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["\n\n", "User:", "###"],
            echo=False
        )
        return response["choices"][0]["text"].strip()

    def generate_json(self, prompt: str) -> str:
        # Mistral-specific prompt format for JSON extraction
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        return self.generate(formatted_prompt, max_tokens=1024, temperature=0.1)

# Singleton instance
engine = LLMEngine()
