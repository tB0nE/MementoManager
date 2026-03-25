import os
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()

model_path = os.getenv("MODEL_PATH", "models/Magistral-Small-2509-Q4_K_M.gguf")
print(f"Testing model at: {model_path}")
print(f"File exists: {os.path.exists(model_path)}")
print(f"File size: {os.path.getsize(model_path) if os.path.exists(model_path) else 'N/A'}")

try:
    print("Attempting to load model...")
    llm = Llama(model_path=model_path, n_gpu_layers=-1, verbose=True)
    print("Success! Model loaded.")
    res = llm("Q: What is 2+2? A:", max_tokens=5)
    print(f"Test generation: {res}")
except Exception as e:
    print(f"Error: {e}")
