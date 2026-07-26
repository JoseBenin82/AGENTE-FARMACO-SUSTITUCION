# 💊 FarmaBot - Agente de Sustitución Farmacéutica

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-producción-green)
![Python](https://img.shields.io/badge/python-3.11+-orange)

> **Agente RAG corporativo** para consultas sobre sustitución de medicamentos en situaciones de desabastecimiento, basado en guías farmacológicas, protocolos clínicos y tablas de equivalencia terapéutica.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación y Uso Local](#-instalación-y-uso-local)
- [Despliegue en OCI](#-despliegue-en-oci)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentos Soportados](#-documentos-soportados)
- [API de Componentes](#-api-de-componentes)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Licencia](#-licencia)

---

## 🎯 Descripción

FarmaBot es un asistente de inteligencia artificial que resuelve la **crisis de desabastecimiento de medicamentos** en tiempo real. Cuando un médico receta un medicamento que no está disponible, FarmaBot consulta guías farmacológicas, protocolos de sustitución y documentos de dosificación para ofrecer alternativas seguras basadas en literatura verificable.

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

---

## 🏗 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaz Streamlit                       │
│                   (Chat Web / Widget)                       │
└─────────────────┬───────────────────────────┬───────────────┘
                  │ Pregunta                   │ Respuesta + Fuentes
┌─────────────────▼───────────────────────────▼───────────────┐
│                      Capa de Generación                     │
│               LLM (Mock / OpenAI / Anthropic)               │
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

- Python 3.11+
- pip
- (Opcional) Docker
- (Opcional) Cuenta en OCI para despliegue cloud

### Variables de Entorno

| Variable | Descripción | Default |
|---|---|---|
| `LLM_PROVIDER` | Proveedor del modelo (`mock`, `openai`, `anthropic`, `ollama`) | `mock` |
| `OPENAI_API_KEY` | API Key de OpenAI | - |
| `ANTHROPIC_API_KEY` | API Key de Anthropic | - |
| `EMBEDDING_MODEL` | Modelo de embeddings | `all-MiniLM-L6-v2` |
| `RERANKER_MODEL` | Modelo de reranking | `ms-marco-MiniLM-L-6-v2` |
| `CHAT_MODEL` | Modelo de chat | `gpt-4o-mini` |
| `CHUNK_SIZE` | Tamaño de chunks en tokens | `600` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `100` |
| `TOP_K_RETRIEVAL` | Candidatos en búsqueda inicial | `20` |
| `TOP_K_FINAL` | Resultados finales tras reranking | `5` |
| `SIMILARITY_THRESHOLD` | Umbral mínimo de similitud | `0.30` |

---

## 🚀 Instalación y Uso Local

```bash
# 1. Clonar repositorio
git clone https://github.com/JoseBenin82/AGENTE-FARMACO-SUSTITUCION.git
cd AGENTE-FARMACO-SUSTITUCION

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env según sea necesario

# 5. Indexar documentos
python scripts/index_documents.py

# 6. Ejecutar la aplicación
streamlit run app/main.py
```

La aplicación estará disponible en `http://localhost:8501`.

---

## ☁️ Despliegue en OCI

### Opción 1: Docker Compose (recomendado)

```bash
# Construir y ejecutar
docker-compose up --build -d
```

### Opción 2: OCI Compute + Docker

1. Crear una instancia compute (VM.Standard.E2.1.Micro - siempre gratuito)
2. Instalar Docker en la instancia
3. Construir y ejecutar:

```bash
docker build -t farmabot .
docker run -d -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e LLM_PROVIDER=mock \
  farmabot
```

4. Abrir el puerto 8501 en el Security List de OCI
5. Acceder a `http://<IP_PUBLICA>:8501`

### Opción 3: OCI Registry + Compute

```bash
# Autenticarse en OCI Registry
docker login <region>.ocir.io

# Taggear y subir imagen
docker tag farmabot:latest <region>.ocir.io/<namespace>/farmabot:latest
docker push <region>.ocir.io/<namespace>/farmabot:latest

# En la instancia OCI
docker pull <region>.ocir.io/<namespace>/farmabot:latest
docker run -d -p 8501:8501 <region>.ocir.io/<namespace>/farmabot:latest
```

### Servicios OCI Utilizados

- **Oracle Compute Instance**: Hosting de la aplicación
- **OCI Registry (OCIR)**: Almacenamiento de imágenes Docker
- **Virtual Cloud Network**: Red y seguridad

> **Nota**: El proyecto usa ChromaDB como base de datos vectorial local (persistente en disco).
> Para escala enterprise, se puede migrar a **OCI OpenSearch** o **Oracle Autonomous Database + pgvector**.

---

## 📁 Estructura del Proyecto

```
AGENTE-FARMACO-SUSTITUCION/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada Streamlit
│   ├── config.py                  # Configuración global
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
│   └── ui/
│       └── chat_ui.py             # Componentes de interfaz Streamlit
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

> *(Insertar aquí captura de pantalla de la aplicación funcionando en OCI)*
>
> *Ejemplo de cómo agregar:*
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
