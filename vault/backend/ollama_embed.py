import requests

from backend.config import (
    OLLAMA_EMBED_URL,
    EMBED_MODEL
)


def get_embedding(text: str):

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBED_MODEL,
            "prompt": text
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["embedding"]