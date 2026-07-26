"""
Script para probar consultas contra el agente.
Uso: python scripts/query_test.py "¿Qué alternativa hay para Losartán?"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from app.retrieval.vector_store import VectorStore
from app.retrieval.reranker import Reranker
from app.generation.responder import LLMResponder

def main():
    parser = argparse.ArgumentParser(description="Consultar FarmaBot")
    parser.add_argument("query", nargs="?", default=None, help="Pregunta a realizar")
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Modo interactivo"
    )
    args = parser.parse_args()

    store = VectorStore()
    reranker = Reranker()
    responder = LLMResponder()

    stats = store.get_collection_stats()
    print(f"[INFO] {stats['total_chunks']} fragmentos indexados\n")

    def process(query: str):
        print(f"[QUERY] {query}")
        candidates = store.search(query, n_results=20)
        top = reranker.rerank(query, candidates, top_k=5)
        respuesta, fuentes = responder.generate(query, top)
        print(f"\n[RESPONSE]\n{respuesta}\n")
        if fuentes:
            print("[SOURCES]")
            for f in fuentes:
                print(f"  - {f}")

    if args.interactive or args.query is None:
        print("[INFO] FarmaBot - Modo interactivo")
        print('Escribe "salir" para terminar\n')
        while True:
            try:
                q = input("Pregunta: ").strip()
                if q.lower() in ("salir", "exit", "quit"):
                    break
                if q:
                    process(q)
                    print()
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        print("\n[INFO] Hasta luego!")
    elif args.query:
        process(args.query)

if __name__ == "__main__":
    main()
