import streamlit as st

def render_chat_interface():
    st.markdown(
        """
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1565c0;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #2e7d32;
    }
    .source-badge {
        display: inline-block;
        background-color: #e8eaf6;
        color: #283593;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])
        css_class = "user-message" if role == "user" else "assistant-message"
        icon = "🧑‍💼" if role == "user" else "🤖"
        with st.container():
            st.markdown(
                f'<div class="chat-message {css_class}">'
                f"<strong>{icon} {role.title()}:</strong><br>{content}",
                unsafe_allow_html=True,
            )
            if role == "assistant" and sources:
                st.markdown("**Fuentes:**")
                cols = st.columns(min(len(sources), 3))
                for i, src in enumerate(sources):
                    with cols[i % 3]:
                        st.markdown(
                            f'<span class="source-badge">📄 {src}</span>',
                            unsafe_allow_html=True,
                        )
            st.markdown("</div>", unsafe_allow_html=True)

def render_sidebar(stats: dict):
    with st.sidebar:
        st.image(
            "https://img.icons8.com/color/96/pill.png",
            width=80,
        )
        st.title("🧬 FarmaBot")
        st.caption("Agente de Sustitución Farmacéutica")
        st.divider()
        st.markdown("### 📊 Estadísticas")
        st.metric("Fragmentos indexados", stats.get("total_chunks", 0))
        st.divider()
        st.markdown("### 📚 Documentos")
        st.markdown("El agente responde basado en:")
        st.markdown("- Guías de sustitución")
        st.markdown("- Tablas de equivalencia")
        st.markdown("- Protocolos clínicos")
        st.markdown("- Políticas farmacéuticas")
        st.divider()
        st.markdown("### ⚙️ Configuración")
        st.caption(f"LLM: {st.session_state.get('llm_provider', 'mock')}")
        st.caption(f"Embeddings: {st.session_state.get('embedding_model', 'all-MiniLM-L6-v2')}")
        st.divider()
        st.markdown("---")
        st.caption("Proyecto ONE - Alura + Oracle")
