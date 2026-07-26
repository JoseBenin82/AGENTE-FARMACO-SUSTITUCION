import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    LLM_PROVIDER,
    EMBEDDING_MODEL,
    TOP_K_RETRIEVAL,
    SIMILARITY_THRESHOLD,
)
from app.retrieval.vector_store import VectorStore
from app.retrieval.reranker import Reranker
from app.generation.responder import LLMResponder

st.set_page_config(
    page_title="FarmaBot - Agente de Sustitución Farmacéutica",
    page_icon="💊",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
if "reranker" not in st.session_state:
    st.session_state.reranker = Reranker()
if "responder" not in st.session_state:
    st.session_state.responder = LLMResponder()
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = LLM_PROVIDER
if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = EMBEDDING_MODEL

def process_query(query: str):
    vector_store = st.session_state.vector_store
    reranker = st.session_state.reranker
    responder = st.session_state.responder

    with st.spinner("🔍 Buscando en documentos..."):
        candidates = vector_store.search(
            query, n_results=TOP_K_RETRIEVAL
        )

    if not candidates:
        respuesta = (
            "No encontré información relevante en los documentos "
            "disponibles para responder tu pregunta."
        )
        fuentes = []
    else:
        with st.spinner("📊 Reclasificando resultados..."):
            top_context = reranker.rerank(query, candidates)

        with st.spinner("🤖 Generando respuesta..."):
            respuesta, fuentes = responder.generate(query, top_context)

    st.session_state.messages.append({
        "role": "assistant",
        "content": respuesta,
        "sources": fuentes,
    })

st.title("💊 FarmaBot - Asistente de Sustitución Farmacéutica")
st.caption(
    "Consulta guías de equivalencia, protocolos de sustitución, "
    "dosificación y más. Basado en documentación farmacéutica verificada."
)

from app.ui.chat_ui import render_chat_interface, render_sidebar

try:
    stats = st.session_state.vector_store.get_collection_stats()
except Exception:
    stats = {"total_chunks": 0}

render_sidebar(stats)
render_chat_interface()

prompt = st.chat_input("Ej: ¿Qué alternativa hay para el medicamento Losartán si no hay stock?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    process_query(prompt)
    st.rerun()
