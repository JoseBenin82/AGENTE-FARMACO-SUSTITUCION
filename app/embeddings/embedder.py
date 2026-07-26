import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

class Embedder:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        model = self._load_model()
        return model.encode(texts, show_progress_bar=False)

    def encode_query(self, query: str) -> np.ndarray:
        model = self._load_model()
        return model.encode([query], show_progress_bar=False)[0]
