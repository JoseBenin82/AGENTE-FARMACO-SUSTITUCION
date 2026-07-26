from sentence_transformers import CrossEncoder
from app.config import RERANKER_MODEL, TOP_K_FINAL

class Reranker:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            self._model = CrossEncoder(RERANKER_MODEL)
        return self._model

    def rerank(
        self, query: str, candidates: list[dict], top_k: int = None
    ) -> list[dict]:
        if top_k is None:
            top_k = TOP_K_FINAL
        if not candidates:
            return []
        model = self._load_model()
        pairs = [(query, c["texto"]) for c in candidates]
        scores = model.predict(pairs)
        for i, c in enumerate(candidates):
            c["score_rerank"] = float(scores[i])
        ranked = sorted(candidates, key=lambda x: x["score_rerank"], reverse=True)
        return ranked[:top_k]
