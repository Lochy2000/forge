# 1. Make sure Ollama is running (open a separate terminal and leave it running)
ollama serve

# 2. Make sure the embedding model is pulled
ollama pull nomic-embed-text

# 3. Activate your virtual environment (from the vault/ directory)
cd vault
.\venv\Scripts\Activate.ps1

# 4. Install dependencies (if switching to a fresh venv)
pip install -r requirements.txt
