import gradio as gr

# --- Compatibility shim -----------------------------------------------------
import gradio_client.utils as _gc_utils

_original_json_schema_to_python_type = _gc_utils._json_schema_to_python_type

def _patched_json_schema_to_python_type(schema, defs=None):
    if isinstance(schema, bool):
        return "Any"
    return _original_json_schema_to_python_type(schema, defs)

_gc_utils._json_schema_to_python_type = _patched_json_schema_to_python_type
# -----------------------------------------------------------------------------

from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response
from ui import (
    CUSTOM_CSS,
    FILL_INPUT_JS,
    LUCIDE_HEAD,
    build_chips,
    build_sidebar,
    build_topbar,
)


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def run_ingestion():
    collection = get_collection()
    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        return
    print("Ingesting source documents...")
    documents = load_documents()
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc["content"], doc["filename"])
        all_chunks.extend(chunks)
    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")
    else:
        print("\n⚠️  No chunks produced.\n")


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    return generate_response(message, retrieved)


def respond(message, history):
    if not message.strip():
        return history, ""
    reply = chat(message, history)
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return history, ""


# ---------------------------------------------------------------------------
# Build UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    theme=gr.themes.Base(),
    title="The Unofficial Guide",
    css=CUSTOM_CSS,
    js=FILL_INPUT_JS,
    head=LUCIDE_HEAD,
) as demo:

    gr.HTML(build_topbar())

    with gr.Row(elem_id="ug-main-row", equal_height=True):

        with gr.Column(elem_id="ug-chat-col", scale=4):
            chatbot = gr.Chatbot(
                elem_id="chat-window",
                type="messages",
                show_label=False,
                placeholder=(
                    "<div style='text-align:center;padding-top:80px;"
                    "color:rgba(255,255,255,0.18);font-size:14px;'>"
                    "🎓<br><br>Ask a question to get started"
                    "</div>"
                ),
                bubble_full_width=False,
                height=520,
            )
            gr.HTML(build_chips())
            with gr.Row(elem_id="ug-input-row"):
                msg = gr.Textbox(
                    elem_id="msg-input",
                    placeholder="Ask about internships, interviews, projects, grad school…",
                    show_label=False,
                    scale=5,
                    lines=1,
                )
                submit = gr.Button("", elem_id="send-btn", scale=0, min_width=44)

        with gr.Column(elem_id="ug-side-col", scale=1, min_width=250):
            gr.HTML(build_sidebar())

    submit.click(respond, [msg, chatbot], [chatbot, msg])
    msg.submit(respond, [msg, chatbot], [chatbot, msg])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  The Unofficial Guide — starting up")
    print("=" * 50 + "\n")
    run_ingestion()
    demo.launch(server_name="127.0.0.1", show_api=False)