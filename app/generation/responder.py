import json
import re
from typing import Optional
from app.config import LLM_PROVIDER, SIMILARITY_THRESHOLD

class MockLLM:
    def generate(self, prompt: str, context: list[dict]) -> str:
        best = context[0] if context else None
        if not best:
            return "No encontré información relevante en los documentos disponibles."
        doc = best["metadata"].get("archivo", "documento")
        seccion = best["metadata"].get("seccion", "")
        texto = best["texto"][:300]
        respuesta = (
            f"Basado en el documento '{doc}'"
            + (f", sección '{seccion}'" if seccion else "")
            + ":\n\n"
            + f"{texto}\n\n"
            + "*Estoy funcionando en modo de demostración (MockLLM). "
            + "Configura LLM_PROVIDER=openai o anthropic para respuestas completas.*"
        )
        return respuesta

class LLMResponder:
    def __init__(self):
        self.mock = MockLLM()
        self._client = None
        self._provider = LLM_PROVIDER
        self._init_provider()

    def _init_provider(self):
        if self._provider == "openai":
            from openai import OpenAI
            from app.config import OPENAI_API_KEY
            self._client = OpenAI(api_key=OPENAI_API_KEY)
        elif self._provider == "anthropic":
            from anthropic import Anthropic
            from app.config import ANTHROPIC_API_KEY
            self._client = Anthropic(api_key=ANTHROPIC_API_KEY)
        elif self._provider == "ollama":
            from openai import OpenAI
            from app.config import OLLAMA_BASE_URL
            self._client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
        elif self._provider == "openrouter":
            from openai import OpenAI
            from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
            self._client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=OPENROUTER_API_KEY,
            )

    def generate(
        self,
        query: str,
        context: list[dict],
        chat_history: Optional[list] = None,
    ) -> tuple[str, list[str]]:
        if self._provider == "mock":
            respuesta = self.mock.generate(query, context)
            fuentes = self._extract_sources(context)
            return respuesta, fuentes
        if not context or context[0].get("similitud", 0) < SIMILARITY_THRESHOLD:
            return (
                "No encontré información suficiente en los documentos "
                "disponibles para responder tu pregunta.",
                [],
            )
        contexto_texto = self._build_context(context)
        system_prompt = (
            "Eres un asistente corporativo de IA especializado en información "
            "farmacéutica y de salud. Responde ÚNICAMENTE con base en el contexto "
            "proporcionado. Si no encuentras la respuesta en el contexto, "
            "dí: 'No encontré esta información en los documentos disponibles.' "
            "Siempre cita la fuente (nombre del archivo y sección) de donde "
            "obtuviste cada parte de la información.\n\n"
            "Contexto:\n" + contexto_texto
        )
        try:
            if self._provider == "openai":
                respuesta = self._call_openai(system_prompt, query)
            elif self._provider == "anthropic":
                respuesta = self._call_anthropic(system_prompt, query)
            elif self._provider == "ollama":
                respuesta = self._call_ollama(system_prompt, query)
            elif self._provider == "openrouter":
                respuesta = self._call_openai(system_prompt, query)
            else:
                respuesta = self.mock.generate(query, context)
        except Exception as e:
            respuesta = f"Error al generar respuesta: {str(e)}"
        fuentes = self._extract_sources(context)
        return respuesta, fuentes

    def _build_context(self, context: list[dict]) -> str:
        parts = []
        for i, c in enumerate(context, 1):
            meta = c["metadata"]
            fuente = (
                f"Fuente {i}: {meta.get('archivo', 'Desconocido')}"
                + (f", Sección: {meta.get('seccion', '')}" if meta.get("seccion") else "")
                + (f", Página: {meta.get('pagina', '')}" if meta.get("pagina") else "")
                + (f", Categoría: {meta.get('categoria', '')}" if meta.get("categoria") else "")
            )
            parts.append(f"{fuente}\nContenido: {c['texto']}\n")
        return "\n---\n".join(parts)

    def _call_openai(self, system_prompt: str, query: str) -> str:
        from app.config import CHAT_MODEL
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = self._client.chat.completions.create(
            model=CHAT_MODEL, messages=messages, temperature=0.1
        )
        return response.choices[0].message.content.strip()

    def _call_anthropic(self, system_prompt: str, query: str) -> str:
        from app.config import CHAT_MODEL
        response = self._client.messages.create(
            model=CHAT_MODEL,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
            max_tokens=1024,
            temperature=0.1,
        )
        return response.content[0].text.strip()

    def _call_ollama(self, system_prompt: str, query: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = self._client.chat.completions.create(
            model="llama3", messages=messages, temperature=0.1
        )
        return response.choices[0].message.content.strip()

    def _extract_sources(self, context: list[dict]) -> list[str]:
        seen = set()
        sources = []
        for c in context:
            meta = c["metadata"]
            archivo = meta.get("archivo", "Desconocido")
            seccion = meta.get("seccion", "")
            key = f"{archivo}:{seccion}"
            if key not in seen:
                seen.add(key)
                source = archivo
                if seccion:
                    source += f" - {seccion}"
                if meta.get("categoria"):
                    source += f" ({meta['categoria']})"
                sources.append(source)
        return sources
