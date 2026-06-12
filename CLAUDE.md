# The Unofficial Guide — CLAUDE.md

CodePath AI201 Project 1. RAG chatbot answering CS student career questions, grounded in 10 curated articles.

## Project structure

```
config.py       — SOURCES catalog, chunk params, model names, API keys via .env
ingest.py       — load_documents() + paragraph-aware chunk_document() (400 char / 80 overlap)
retriever.py    — embed_and_store() + retrieve() via ChromaDB + all-MiniLM-L6-v2
generator.py    — generate_response(): grounding system prompt + programmatic source citation
ui/
  __init__.py   — public exports
  components.py — build_topbar(), build_sidebar(), build_chips(), EXAMPLE_QUESTIONS, SOURCE_ICONS
  styles.py     — CUSTOM_CSS
  scripts.py    — FILL_INPUT_JS (page-load JS), LUCIDE_HEAD
app.py          — thin controller: ingestion bootstrap, chat()/respond(), gr.Blocks layout wiring
documents/      — 10 .txt source files
chroma_db/      — persisted vector store (auto-populated on first run)
```

## Running

```bash
source .venv/bin/activate
python app.py
# → http://127.0.0.1:7860
```

Vector store auto-populates on first run if empty. Re-ingest by deleting `chroma_db/`.

## Architecture (MVVM-style)

- **View** → `ui/` package (HTML, CSS, JS — nothing about retrieval or generation)
- **Model** → `retriever.py`, `generator.py`, `config.py`, `ingest.py`
- **Controller** → `app.py` (wires Gradio events to the model layer, owns ingestion bootstrap)

## Key Gradio 4.44 quirks

- `gr.Blocks()` has no `elem_id` — anchor layout CSS on `gr.Row(elem_id=...)` instead.
- `<script>` in `gr.HTML()` never executes — put page-load JS in `gr.Blocks(js=...)`.
- `.flex-wrap` on each bubble carries Gradio's default panel background — strip it in CSS.
- Chat auto-scroll target is `.bubble-wrap` (internal scroll container, not the page).
- Lucide icons: use bounded `setInterval` poll for `lucide.createIcons()`, NOT MutationObserver (feedback loop).
- Column height: add `height: 100% !important; max-height: 100% !important` to counteract Gradio's inline `flex-grow` from `scale=`.
- Chip onclick strings: use `html.escape(json.dumps(q))`, never `repr(q)` (breaks on apostrophes).

## Grounding pattern

System prompt enforces answer-from-context-only with an exact fallback string.
`generate_response()` detects refusal by string match → skips Sources section.
Context passed as plain unlabeled text — no `[1]` indices or filenames (model echoes them back).
Sources appended programmatically after generation, never left to the LLM.

## Stack

Python 3.9 · Gradio 4.44 · ChromaDB · sentence-transformers (`all-MiniLM-L6-v2`) · Groq API (llama-3.3-70b-versatile) · Lucide icons (CDN)
