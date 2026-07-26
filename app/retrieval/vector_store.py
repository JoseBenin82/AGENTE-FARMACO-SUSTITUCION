import chromadb
from chromadb.config import Settings
import numpy as np
from typing import Optional
from app.config import VECTOR_DB_PATH, COLLECTION_NAME
from app.embeddings.embedder import Embedder

class VectorStore:
    _instance = None
    _collection = None
    _embedder = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._embedder is None:
            self._embedder = Embedder()
            self._client = chromadb.PersistentClient(
                path=str(VECTOR_DB_PATH),
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

    def add_chunks(self, chunks: list[dict]):
        texts = [c["texto"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [c["metadata"]["chunk_id"] for c in chunks]
        embeddings = self._embedder.encode(texts)
        self._collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids,
        )

    def search(
        self,
        query: str,
        n_results: int = 20,
        filter_metadata: Optional[dict] = None,
    ) -> list[dict]:
        query_embedding = self._embedder.encode_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "texto": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distancia": results["distances"][0][i],
                "similitud": 1 - results["distances"][0][i],
            })
        return hits

    def get_collection_stats(self) -> dict:
        count = self._collection.count()
        return {"total_chunks": count}

    def reset_collection(self):
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        type(self)._instance = None
        type(self)._collection = None
