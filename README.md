# 💊 FarmaBot - Agente de IA Corporativo (RAG) para Sustitución Farmacéutica

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-producción-green)
![Python](https://img.shields.io/badge/python-3.13+-orange)

> **Challenge Final Alura ONE** — Agente de IA corporativo con RAG (Retrieval-Augmented Generation) que permite a cualquier colaborador hacer preguntas en lenguaje natural sobre documentos internos y recibir respuestas directas con fuentes verificables. Este agente está especializado en el rubro farmacéutico: resuelve consultas sobre sustitución de medicamentos en situaciones de desabastecimiento, basado en guías farmacológicas, protocolos clínicos y tablas de equivalencia terapéutica.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Tecnologías](#-tecnologías)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación y Uso Local](#-instalación-y-uso-local)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentos Soportados](#-documentos-soportados)
- [API de Componentes](#-api-de-componentes)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Licencia](#-licencia)

---

## 🎯 Descripción

### El problema real

En muchas empresas, los colaboradores pierden horas buscando información dentro de manuales, informes, políticas y hojas de cálculo internas. La información existe, pero está dispersa en archivos y formatos. Este proyecto resuelve ese problema construyendo un **agente de IA corporativo** que cualquier persona puede usar para hacer preguntas en lenguaje natural y recibir respuestas directas, citando la fuente exacta del documento.

### El caso farmacéutico

Aplicamos esta solución al rubro farmacéutico: cuando un médico receta un medicamento que no está disponible por desabastecimiento, FarmaBot consulta guías farmacológicas, protocolos de sustitución y tablas de dosificación para ofrecer alternativas seguras basadas en literatura verificable.

### ¿Qué problema resuelve?

- **Escasez de medicamentos**: Crisis global de desabastecimiento de fármacos.
- **Búsqueda manual**: Revisar guías de equivalencia, calcular nuevas dosis y asegurar que la alternativa no cause alergias o interacciones.
- **Seguridad**: Validación contra alergias, función renal, interacciones y contraindicaciones.

### Ejemplo de uso

```
Usuario: "No hay Losartán 50 mg. El paciente toma Enalapril y Metformina, y tiene insuficiencia renal estadio 3a."

FarmaBot: "Según la Guía de Sustitución de Antihipertensivos v2.1 y el Protocolo de Ajuste Renal v3.0:

1. Alternativa sugerida: Valsartán 80 mg cada 24h
2. Equivalente a Losartán 50 mg (Tabla de Equivalencias Terapéuticas)
3. No requiere ajuste renal para Valsartán (CrCl >30)
4. No se identifican interacciones con Enalapril ni Metformina

Fuentes: guia_sustitucion_antihipertensivos.md (Sección 3.2),
         protocolo_ajuste_renal.md (Sección 3.2),
         equivalentias_terapeuticas.json"
```

### Otras preguntas que puede responder

| Pregunta | Fuente utilizada |
|----------|------------------|
| "¿Qué alternativas hay para Enapril 10 mg?" | Guía de sustitución de antihipertensivos |
| "¿Cómo ajustar dosis de Metformina en ERC etapa 3b?" | Protocolo de ajuste renal |
| "¿Cuál es la dosis máxima de Paracetamol en adultos mayores?" | Tabla de equivalentes analgésicos |
| "Mostrar el procedimiento ante desabastecimiento de Losartán" | SOP de dispensación |
| "¿Qué medicamentos están contraindicados con Warfarina?" | Guía de interacciones medicamentosas |

---

## 🛠 Tecnologías

| Tecnología | Propósito |
|------------|-----------|
| **Python 3.13+** | Lenguaje principal |
| **LangChain** | Framework de orquestación del agente (prompting, encadenamiento LLM, parser de salida) |
| **OpenRouter** | API unificada para modelos LLM (GPT-4o, Claude, Llama 3, Mistral, etc.) |
| **ChromaDB** | Base de datos vectorial local (índice HNSW, búsqueda por similitud coseno) |
| **Sentence-Transformers** | Modelos de embeddings (`all-MiniLM-L6-v2`) y reranker cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| **FastAPI + Uvicorn** | Servidor web ASGI para la API REST |
| **PyMuPDF / python-docx / openpyxl / python-pptx** | Extracción de texto desde PDF, Word, Excel y PowerPoint |
| **BeautifulSoup / markdown** | Extracción de texto desde HTML y Markdown |
| **Docker** | Contenedor para despliegue en OCI |
| **OCI Compute** | Infraestructura cloud (opcional) |

---

## 🏗 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│              Interfaz Web (HTML + CSS + JS)                 │
│               FastAPI + Uvicorn (backend API)               │
└─────────────────┬───────────────────────────┬───────────────┘
                  │ Pregunta                   │ Respuesta + Fuentes
┌─────────────────▼───────────────────────────▼───────────────┐
│                   Capa de Generación (LangChain)             │
│        ChatOpenAI + ChatPromptTemplate + StrOutputParser    │
│         OpenRouter (GPT-4o, Claude, Llama, etc.)           │
│        Genera respuesta + Cita fuentes + Validación        │
└────────────────────────────┬───────────────────────────────┘
                             │ Contexto recuperado
┌────────────────────────────▼───────────────────────────────┐
│                   Capa de Recuperación                      │
│           Búsqueda Semántica → Reranking (Cross-encoder)   │
└────────────────────────────┬───────────────────────────────┘
                             │ Query embedding
┌────────────────────────────▼───────────────────────────────┐
│                  Indexación Vectorial                       │
│           Sentence-Transformers + ChromaDB (HNSW)          │
│           Embeddings + Metadata + Índice coseno            │
└────────────────────────────┬───────────────────────────────┘
                             │ Chunks + Metadata
┌────────────────────────────▼───────────────────────────────┐
│               Procesamiento de Documentos                   │
│  Extracción → Limpieza → Chunking (tokens, overlap, 600t) │
│  PDF | Word | Excel | PPT | MD | CSV | JSON | HTML        │
└────────────────────────────┬───────────────────────────────┘
                             │ Documentos originales
┌────────────────────────────▼───────────────────────────────┐
│              Documentos Farmacéuticos                       │
│  Guías | Protocolos | Tablas | Políticas | SOPs           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Requisitos

- Python 3.13+
- pip
- (Opcional) Docker
- (Opcional) Cuenta en OCI para despliegue cloud

### Variables de Entorno

| Variable | Descripción | Default |
|---|---|---|
| `LLM_PROVIDER` | Proveedor del modelo (`openrouter`, `openai`, `anthropic`, `ollama`, `mock`) | `openrouter` |
| `OPENROUTER_API_KEY` | API Key de OpenRouter | - |
| `OPENROUTER_BASE_URL` | URL base de OpenRouter | `https://openrouter.ai/api/v1` |
| `OPENAI_API_KEY` | API Key de OpenAI | - |
| `ANTHROPIC_API_KEY` | API Key de Anthropic | - |
| `OLLAMA_BASE_URL` | URL base de Ollama (local) | `http://localhost:11434` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `all-MiniLM-L6-v2` |
| `RERANKER_MODEL` | Modelo de reranking | `ms-marco-MiniLM-L-6-v2` |
| `CHAT_MODEL` | Modelo de chat. OpenRouter: `proveedor/modelo`, usa sufijo `:free` para modelos gratuitos o `openrouter/free` para auto-routing | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `CHUNK_SIZE` | Tamaño de chunks en tokens | `600` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `100` |
| `TOP_K_RETRIEVAL` | Candidatos en búsqueda inicial | `20` |
| `TOP_K_FINAL` | Resultados finales tras reranking | `5` |
| `SIMILARITY_THRESHOLD` | Umbral mínimo de similitud | `0.30` |
| `LLM_TEMPERATURE` | Temperatura del modelo | `0.1` |
| `LLM_MAX_TOKENS` | Máximo de tokens en respuesta | `1024` |
| `VECTOR_DB_PATH` | Ruta de la base de datos vectorial | `data/chroma_db` |
| `COLLECTION_NAME` | Nombre de la colección en ChromaDB | `farmaco_docs` |
| `DOCUMENTS_PATH` | Ruta de los documentos a indexar | `data/documents` |

---

## 🚀 Instalación y Uso Local

### 1. Requisitos previos

- **Python 3.13+** instalado (`python --version`)
- **pip** incluido con Python
- ~2 GB de espacio libre en disco (modelos de embeddings y reranker se descargan automáticamente)

### 2. Clonar e instalar

```bash
# Clonar el repositorio
git clone https://github.com/JoseBenin82/AGENTE-FARMACO-SUSTITUCION.git
cd AGENTE-FARMACO-SUSTITUCION

# Crear y activar entorno virtual
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
# venv\Scripts\activate.bat

# Linux / macOS:
# source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Abre `.env` y configura al menos `LLM_PROVIDER`:

#### Modo mock (sin API key — recomendado para probar)

```env
LLM_PROVIDER=mock
```

Este modo usa un `MockLLM` interno que devuelve el fragmento más relevante del contexto sin llamar a ningún API externa. No necesitas ninguna API key.

#### Modo OpenRouter (recomendado para uso real)

1. Regístrate en [OpenRouter.ai](https://openrouter.ai)
2. Genera una API key en [https://openrouter.ai/keys](https://openrouter.ai/keys)
3. Configura en `.env`:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-tu-api-key-aqui
CHAT_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

> **Modelos gratuitos**: Puedes usar cualquier modelo gratuito de OpenRouter agregando el sufijo `:free` (ej. `google/gemma-4-26b-a4b-it:free`, `openai/gpt-oss-20b:free`) o usar el router automático `openrouter/free` para que seleccione el mejor disponible.

#### Otros proveedores

| Proveedor | `LLM_PROVIDER` | Requiere |
|-----------|----------------|----------|
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` |
| Ollama (local) | `ollama` | `OLLAMA_BASE_URL` (default: `http://localhost:11434`) |

> Todos los modelos de embeddings y reranker se descargan automáticamente la primera vez desde Hugging Face.

### 4. Indexar documentos

Este paso procesa los documentos en `data/documents/`, los divide en fragmentos y los almacena en ChromaDB:

```bash
python scripts/index_documents.py
```

La primera ejecución descarga los modelos `all-MiniLM-L6-v2` y `ms-marco-MiniLM-L-6-v2` (~200 MB total). El indexado debe completarse en segundos.

Para reindexar desde cero (útil si agregas o modificas documentos):

```bash
python scripts/index_documents.py --reset
```

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El flag `--reload` reinicia el servidor automáticamente al detectar cambios en el código (útil durante desarrollo).

Abre en tu navegador: **[http://localhost:8000](http://localhost:8000)**

### 6. Probar sin interfaz web (CLI)

Para hacer consultas directas desde terminal sin abrir el navegador:

```bash
# Consulta única
python scripts/query_test.py "¿Qué alternativa hay para Losartán?"

# Modo interactivo
python scripts/query_test.py -i
```

Escribe `salir` para terminar el modo interactivo.

### Solución de problemas

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| `ModuleNotFoundError` | Entorno virtual no activado | Activa el venv con el comando correspondiente a tu sistema |
| `Error al generar respuesta con LangChain` | API key inválida o sin saldo | Usa `LLM_PROVIDER=mock` para probar sin API key |
| El navegador no carga la página | Puerto 8000 en uso | Usa `--port 8001` o detén el proceso que ocupa el puerto |
| `No encontré información...` en todas las consultas | Documentos no indexados | Ejecuta `python scripts/index_documents.py` |
| Primera consulta tarda ~30-40s | Inicialización de LangChain | Normal en el primer uso. Las siguientes consultas son rápidas. |
| `Failed to fetch` en el navegador | Servidor aún iniciando o timeout por primera consulta | Espera ~40s y recarga la página |

---

## 📁 Estructura del Proyecto

```
AGENTE-FARMACO-SUSTITUCION/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── config.py                  # Configuración global
│   ├── static/                    # Frontend HTML/CSS/JS
│   ├── document_processor/        # Extracción y procesamiento
│   │   ├── extractor.py           # Interfaz unificada de extracción
│   │   ├── pdf_extractor.py       # PDF (PyMuPDF)
│   │   ├── word_extractor.py      # Word (python-docx)
│   │   ├── excel_extractor.py     # Excel (openpyxl)
│   │   ├── ppt_extractor.py       # PowerPoint (python-pptx)
│   │   ├── markdown_extractor.py  # Markdown → HTML → texto
│   │   ├── csv_extractor.py       # CSV estructurado
│   │   ├── json_extractor.py      # JSON → texto plano
│   │   ├── html_extractor.py      # HTML (BeautifulSoup)
│   │   ├── cleaner.py             # Limpieza de texto
│   │   └── chunker.py             # Chunking por tokens + estructura
│   ├── embeddings/
│   │   └── embedder.py            # Sentence-Transformers embeddings
│   ├── retrieval/
│   │   ├── vector_store.py        # ChromaDB (HNSW, metadata filtering)
│   │   └── reranker.py            # Cross-encoder reranking
│   ├── generation/
│   │   └── responder.py           # LLM con citas, validación y fallback
├── data/
│   ├── documents/                 # Documentos originales
│   │   ├── guias_sustitucion/     # Guías de sustitución terapéutica
│   │   ├── protocolos_clinicos/   # Protocolos y guías clínicas
│   │   ├── tablas_equivalencia/   # Tablas de equivalencias
│   │   ├── politicas_calidad/     # Políticas de calidad
│   │   ├── procedimientos_operativos/  # SOPs
│   │   └── comunicados_internos/  # Comunicados y alertas
│   └── chroma_db/                 # Base de datos vectorial (persistente)
├── scripts/
│   ├── index_documents.py         # Indexación batch de documentos
│   └── query_test.py              # Pruebas de consulta
├── Dockerfile                     # Imagen Docker
├── docker-compose.yml             # Orquestación Docker
├── oci_setup.sh                   # Script de despliegue OCI
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore                     # Archivos ignorados (.env, chroma_db, etc.)
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

---

## 📄 Documentos Soportados

| Formato | Librería | Tipo de Contenido |
|---|---|---|
| PDF | PyMuPDF | Guías, protocolos |
| Word (.docx) | python-docx | Políticas, informes |
| Excel (.xlsx) | openpyxl | Tablas de equivalencia, precios |
| PowerPoint (.pptx) | python-pptx | Presentaciones, capacitaciones |
| Markdown (.md) | markdown + BeautifulSoup | Documentación técnica |
| CSV | csv (stdlib) | Datos tabulares, catálogos |
| JSON | json (stdlib) | Datos estructurados, configuraciones |
| HTML | BeautifulSoup | Políticas, comunicados web |

---

## 🔧 API de Componentes

### Document Processor

```python
from app.document_processor import extract_text, clean_text, chunk_text

# Extraer texto de cualquier formato
text, ext = extract_text("documento.pdf")

# Limpiar y normalizar
clean = clean_text(text)

# Chunking con metadata
chunks = chunk_text(clean, {"archivo": "doc.pdf", "categoria": "guias"})
```

### Vector Store

```python
from app.retrieval.vector_store import VectorStore

store = VectorStore()
store.add_chunks(chunks)
results = store.search("alternativa para Losartán", n_results=10)
```

### Reranker

```python
from app.retrieval.reranker import Reranker

reranker = Reranker()
top = reranker.rerank("¿Qué alternativa hay?", results, top_k=5)
```

### Responder

```python
from app.generation.responder import LLMResponder

responder = LLMResponder()
respuesta, fuentes = responder.generate("¿Qué alternativa hay?", top_context)
```

---

## 📸 Capturas de Pantalla

> *(Pendiente — Insertar aquí captura de pantalla de la aplicación funcionando en OCI)*
>
> Una vez realizado el deploy en OCI, agregar una captura con:
> ```markdown
> ![FarmaBot en OCI](assets/screenshot_oci.png)
> ```

---

## 📜 Licencia

Este proyecto fue desarrollado como parte del programa **ONE (Oracle Next Education)** de **Alura Latam + Oracle**.

---

<div align="center">
  <sub>Proyecto de desafío - Agente de IA Corporativo con RAG</sub>
  <br>
  <sub>© 2025 - Todos los derechos reservados</sub>
</div>
