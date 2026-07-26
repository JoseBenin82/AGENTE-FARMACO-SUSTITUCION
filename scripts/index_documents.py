"""
Script para indexar todos los documentos en la base de datos vectorial.
Uso: python scripts/index_documents.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pathlib import Path
import time
from app.config import DOCUMENTS_PATH, COLLECTION_NAME
from app.document_processor import extract_text, clean_text, chunk_text
from app.retrieval.vector_store import VectorStore

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html", ".htm"}

def index_all_documents():
    vector_store = VectorStore()
    docs_path = Path(DOCUMENTS_PATH)
    if not docs_path.exists():
        print(f"[ERROR] Ruta no encontrada: {docs_path}")
        return 0, 0
    all_files = []
    for ext in SUPPORTED_EXTENSIONS:
        all_files.extend(docs_path.rglob(f"*{ext}"))
    if not all_files:
        print(f"[INFO] No se encontraron documentos en {docs_path}")
        return 0, 0
    print(f"[INFO] Documentos encontrados: {len(all_files)}")
    total_chunks = 0
    indexed_files = 0
    for filepath in sorted(all_files):
        try:
            rel_path = filepath.relative_to(docs_path)
            category = rel_path.parts[0] if len(rel_path.parts) > 1 else "general"
            metadata = {
                "archivo": str(rel_path),
                "categoria": category,
                "formato": filepath.suffix.lower(),
            }
            print(f"  [PROC] Procesando: {rel_path}...", end=" ")
            raw_text, ext = extract_text(str(filepath))
            cleaned = clean_text(raw_text)
            if not cleaned.strip():
                print("[WARN] vacio")
                continue
            chunks = chunk_text(cleaned, metadata)
            if chunks:
                vector_store.add_chunks(chunks)
                total_chunks += len(chunks)
                indexed_files += 1
                print(f"[OK] {len(chunks)} chunks")
            else:
                print("[WARN] sin chunks")
        except Exception as e:
            print(f"[ERROR] {e}")
    print(f"\n[OK] Indexacion completada: {indexed_files} archivos, {total_chunks} chunks")
    return indexed_files, total_chunks

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reiniciar la coleccion antes de indexar")
    args = parser.parse_args()
    print(f"[INFO] Indexando documentos desde: {DOCUMENTS_PATH}")
    print(f"[INFO] Coleccion: {COLLECTION_NAME}")
    if args.reset:
        from app.retrieval.vector_store import VectorStore
        VectorStore().reset_collection()
        print("[INFO] Coleccion reiniciada")
    start = time.time()
    index_all_documents()
    elapsed = time.time() - start
    print(f"[INFO] Tiempo total: {elapsed:.2f}s")
