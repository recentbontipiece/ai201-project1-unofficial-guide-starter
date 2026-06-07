import html
import json

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

from config import SOURCES
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response


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


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EXAMPLE_QUESTIONS = [
    "How do I get a first internship with no experience?",
    "Is LeetCode alone enough for big tech?",
    "What projects actually impress recruiters?",
    "Is a Master's in CS worth it?",
    "How do students handle imposter syndrome?",
    "How do I start contributing to open source?",
]

# Lucide (https://lucide.dev) icon names — rendered client-side via the
# Lucide CDN script (see LUCIDE_HEAD), replacing <i data-lucide="..."> tags
# with inline outline SVGs. Using a shared icon set instead of emoji keeps
# the sidebar visually consistent across platforms/fonts.
SOURCE_ICONS = {
    "First CS Internship Guide":  "briefcase",
    "LeetCode Isn't Enough":      "puzzle",
    "Resume Project Ideas":       "wrench",
    "Master's Degree Worth It?":  "graduation-cap",
    "Imposter Syndrome":          "brain",
    "Technical Interview Prep":   "clipboard-list",
    "Open Source Contribution":   "git-branch",
    "GitHub Portfolio Guide":     "user",
    "CS Student Advice (HN)":     "message-circle",
    "Job Market Prep (HN)":       "trending-up",
}

def get_icon_name(source):
    return SOURCE_ICONS.get(source.get("display_name", ""), "file-text")


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def build_topbar():
    return f"""
<div id="ug-topbar">
  <div id="ug-topbar-left">
    <div id="ug-topbar-icon"><i data-lucide="graduation-cap"></i></div>
    <div>
      <div id="ug-topbar-title">The Unofficial Guide</div>
      <div id="ug-topbar-sub">CS student advice from real discussions</div>
    </div>
  </div>
  <div id="ug-topbar-badge"><i data-lucide="book-open"></i> {len(SOURCES)} sources loaded</div>
</div>"""

def build_sidebar():
    items = "".join(
        f'<a class="ug-sb-item" href="{s["url"]}" target="_blank" rel="noopener noreferrer">'
        f'<span class="ug-sb-icon"><i data-lucide="{get_icon_name(s)}"></i></span>'
        f'<span>{s["display_name"]}</span>'
        f'</a>'
        for s in SOURCES
    )
    return f"""
<div id="ug-sidebar">
  <div id="ug-sb-head"><i data-lucide="library"></i> Sources ({len(SOURCES)})</div>
  <div id="ug-sb-list">{items}</div>
  <div id="ug-sb-note">
    Answers are grounded in these sources only.
    If something isn't covered, the assistant says so rather than guessing.
  </div>
</div>"""

def build_chips():
    buttons = "".join(
        # json.dumps gives a JS-safe double-quoted string literal (escaping
        # any embedded quotes); html.escape then makes that safe to sit
        # inside the onclick="..." HTML attribute (also double-quoted).
        # repr() alone broke on questions with apostrophes — Python's repr
        # would wrap those in double quotes too, prematurely closing the
        # surrounding HTML attribute and corrupting the handler.
        f'<button class="ug-chip" onclick="ugFillInput({html.escape(json.dumps(q))})">{html.escape(q)}</button>'
        for q in EXAMPLE_QUESTIONS
    )
    return f'<div id="ug-chips">{buttons}</div>'


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* Page background */
body, .gradio-container {
    background: #0d0d12 !important;
    font-family: 'DM Sans', sans-serif !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide all the Gradio padding/chrome */
.gradio-container > .main > .wrap { padding: 0 !important; }
footer { display: none !important; }

/* Only flatten spacing on OUR layout containers — not Gradio's internal
   component wrappers (which also use .gap/.contain and need their own
   padding/gap to size inputs like the Textbox correctly). Targeting them
   globally was collapsing the message textarea to 0x0. */
#ug-main-row.contain,
#ug-chat-col.contain,
#ug-side-col.contain { padding: 0 !important; }

#ug-main-row.gap,
#ug-chat-col.gap { gap: 0 !important; }

/* ── Topbar ── */
#ug-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 60px;
    background: #18181f;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    flex-shrink: 0;
}
#ug-topbar-left { display: flex; align-items: center; gap: 12px; }
#ug-topbar-icon {
    width: 36px; height: 36px;
    background: #6c63f6;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
#ug-topbar-title {
    font-size: 15px; font-weight: 600;
    color: #f0f0f5; letter-spacing: -0.01em;
}
#ug-topbar-sub { font-size: 12px; color: rgba(255,255,255,0.38); margin-top: 1px; }
#ug-topbar-badge {
    font-size: 11.5px; padding: 4px 14px; border-radius: 20px;
    background: rgba(108,99,246,0.15);
    border: 1px solid rgba(108,99,246,0.35);
    color: #b0a6ff;
}

/* ── Body row (chat + sidebar) ── */
#ug-body {
    display: flex;
    flex: 1;
    overflow: hidden;
    min-height: 0;
}

/* ── Chat panel ── */
#ug-chat-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
}

/* Chatbot component */
#chat-window {
    flex: 1 !important;
    background: #12121a !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 24px !important;
    overflow-y: auto !important;
}
#chat-window > div { height: 100% !important; }

/* Message bubbles */
#chat-window .message-wrap {
    padding: 0 !important;
    gap: 18px !important;
}
/* Gradio wraps each bubble in a `.flex-wrap` panel that carries its own
   background/border/radius — that's the "card behind the card" the chat
   bubbles were showing. Strip it so only our styled `.message` bubble
   (targeted via [data-testid] below, since its direct child is a <button>
   not a <div>) is visible. */
#chat-window .flex-wrap {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
}
#chat-window .message.bot > div,
#chat-window [data-testid="bot"] {
    background: #1e1e2c !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 4px 14px 14px 14px !important;
    color: #d4d4e8 !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    padding: 13px 16px !important;
    max-width: 84% !important;
    font-family: 'DM Sans', sans-serif !important;
}
#chat-window .message.user > div,
#chat-window [data-testid="user"] {
    background: #6c63f6 !important;
    border: none !important;
    border-radius: 14px 14px 4px 14px !important;
    color: #fff !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    padding: 11px 15px !important;
    max-width: 78% !important;
    margin-left: auto !important;
    font-family: 'DM Sans', sans-serif !important;
}
#chat-window .avatar-container { display: none !important; }
#chat-window .bot a {
    color: #a99eff !important;
    text-decoration: none !important;
    border-bottom: 1px solid rgba(169,158,255,0.35) !important;
}
#chat-window .bot a:hover { border-color: #a99eff !important; }

/* ── Chips ── */
#ug-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    padding: 12px 20px 0;
    background: #18181f;
}
.ug-chip {
    font-size: 12px !important;
    padding: 5px 13px !important;
    border-radius: 20px !important;
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.5) !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.15s !important;
}
.ug-chip:hover {
    background: rgba(108,99,246,0.18) !important;
    border-color: rgba(108,99,246,0.45) !important;
    color: #c0b8ff !important;
}

/* ── Input row ── */
#ug-input-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
    padding: 12px 20px 16px;
    background: #18181f;
    border-top: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0 !important;
    min-height: 66px !important;
}

#msg-input {
    flex: 1 1 auto !important;
    min-height: 42px !important;
}
#msg-input > label.container,
#msg-input .form,
#msg-input .block {
    min-height: 42px !important;
    height: auto !important;
    overflow: visible !important;
}
#msg-input textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #f0f0f5 !important;
    font-size: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
    resize: none !important;
    min-height: 42px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
#msg-input textarea:focus {
    border-color: rgba(108,99,246,0.65) !important;
    box-shadow: 0 0 0 3px rgba(108,99,246,0.14) !important;
    outline: none !important;
}
#msg-input textarea::placeholder { color: rgba(255,255,255,0.22) !important; }

/* Circular icon-only send button. The arrow glyph is an inline-SVG data URI
   used as a CSS mask so it inherits `background-color` (i.e. button text
   color) — this avoids depending on Lucide's JS running inside Gradio's
   own Button component, which renders its label as escaped plain text. */
#send-btn {
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    padding: 0 !important;
    background: #6c63f6 !important;
    border: none !important;
    border-radius: 50% !important;
    color: transparent !important;
    font-size: 0 !important;
    cursor: pointer !important;
    transition: background 0.15s, transform 0.1s !important;
    flex-shrink: 0 !important;
    position: relative !important;
}
#send-btn::before {
    content: "" !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    width: 18px !important;
    height: 18px !important;
    transform: translate(-50%, -50%) !important;
    background-color: #fff !important;
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='19' x2='12' y2='5'%3E%3C/line%3E%3Cpolyline points='5 12 12 5 19 12'%3E%3C/polyline%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='19' x2='12' y2='5'%3E%3C/line%3E%3Cpolyline points='5 12 12 5 19 12'%3E%3C/polyline%3E%3C/svg%3E") !important;
    -webkit-mask-repeat: no-repeat !important;
    mask-repeat: no-repeat !important;
    -webkit-mask-position: center !important;
    mask-position: center !important;
}
#send-btn:hover { background: #5750d4 !important; }
#send-btn:active { transform: scale(0.94) !important; }

/* ── Sidebar ── */
#ug-sidebar {
    width: 250px;
    flex-shrink: 0;
    background: #18181f;
    border-left: 1px solid rgba(255,255,255,0.07);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
#ug-sb-head {
    padding: 16px 16px 12px;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0;
}
#ug-sb-list {
    flex: 1;
    overflow-y: auto;
    padding: 10px 8px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.08) transparent;
}
.ug-sb-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 10px;
    border-radius: 10px;
    font-size: 12.5px;
    color: rgba(255,255,255,0.55);
    text-decoration: none !important;
    transition: background 0.12s, color 0.12s;
    font-family: 'DM Sans', sans-serif;
}
.ug-sb-item:hover {
    background: rgba(108,99,246,0.14);
    color: #c0b8ff;
}
.ug-sb-icon {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: rgba(108,99,246,0.14);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #a99eff;
}
.ug-sb-item:hover .ug-sb-icon {
    background: rgba(108,99,246,0.28);
    color: #c0b8ff;
}
.ug-sb-icon svg, #ug-topbar-icon svg, #ug-topbar-badge svg, #ug-sb-head svg {
    width: 14px;
    height: 14px;
    stroke-width: 2px;
}
#ug-topbar-icon svg { width: 18px; height: 18px; color: #fff; }
#ug-topbar-badge { display: inline-flex !important; align-items: center; gap: 6px; }
#ug-topbar-badge svg { width: 13px; height: 13px; color: #b0a6ff; }
#ug-sb-head { display: flex !important; align-items: center; gap: 6px; }
#ug-sb-head svg { color: rgba(255,255,255,0.32); }
#ug-sb-note {
    margin: 8px 12px 16px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    font-size: 11.5px;
    color: rgba(255,255,255,0.28);
    line-height: 1.55;
    flex-shrink: 0;
}

/* ── Outer wrapper that Gradio generates ── */
/* gr.Blocks has no `elem_id` — it's silently dropped, so #ug-root never
   exists in the DOM. Anchor the height-constraining chain on #ug-main-row
   instead (a real gr.Row, whose elem_id IS applied), walking up via :has()
   so we only constrain the wrappers that actually contain our layout —
   not every .wrap/.gap under .main, which are reused by every component's
   internal layout (including the Textbox's, where overflow:hidden was
   clipping the message input to 0x0). */
.gradio-container .main { height: 100vh !important; display: flex !important; flex-direction: column !important; }
.gradio-container .main > .wrap { flex: 1 !important; min-height: 0 !important; display: flex !important; flex-direction: column !important; overflow: hidden !important; padding: 0 !important; }
/* Any wrapper between .wrap and our row (.contain, .gap, at any depth)
   needs to be height-constrained too, or the row sizes to its content
   instead of the available viewport space. :has() lets us scope this to
   only the wrappers that actually contain #ug-main-row. */
.gradio-container .main > .wrap :has(> #ug-main-row),
.gradio-container .main > .wrap :has(> * > #ug-main-row),
.gradio-container .main > .wrap :has(> * > * > #ug-main-row) {
    flex: 1 !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

/* Row containing chat + sidebar */
#ug-main-row {
    flex: 1 !important;
    min-height: 0 !important;
    display: flex !important;
    overflow: hidden !important;
    gap: 0 !important;
    border: none !important;
    padding: 0 !important;
}
#ug-main-row > .gap { gap: 0 !important; }

/* Chat column inside the row */
/* height/max-height: 100% force the column to the row's cross-size —
   align-items:stretch alone wasn't enough because Gradio's inline
   `flex-grow: 4` (from scale=4) plus content height created a feedback
   loop where the row grew to fit the column and the column grew to fit
   its (unconstrained) content. */
#ug-chat-col {
    flex: 1 !important;
    height: 100% !important;
    max-height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    min-width: 0 !important;
    padding: 0 !important;
    border: none !important;
    gap: 0 !important;
}

/* Sidebar column */
#ug-side-col {
    flex-shrink: 0 !important;
    height: 100% !important;
    max-height: 100% !important;
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;
    padding: 0 !important;
    border: none !important;
}

/* Chatbot fill its column */
#chat-window {
    flex: 1 !important;
    min-height: 0 !important;
    height: auto !important;
    max-height: none !important;
    overflow-y: auto !important;
}
"""


# ---------------------------------------------------------------------------
# JS / head helpers
# ---------------------------------------------------------------------------

# Gradio executes `js=` on page load; <script> tags inside gr.HTML do not run
# because the browser sets that markup via innerHTML, which never executes
# embedded scripts. Defining ugFillInput here makes it a real global function
# the chip buttons' inline onclick handlers can call.
FILL_INPUT_JS = """
function() {
    window.ugFillInput = function(text) {
        var ta = document.querySelector('#msg-input textarea');
        if (!ta) return;
        var nativeInput = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
        nativeInput.set.call(ta, text);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.focus();
    };

    // Lucide replaces <i data-lucide="..."> placeholders with inline SVGs,
    // but our icons live inside gr.HTML blocks that render asynchronously
    // after Lucide's own script loads — so a single createIcons() on page
    // load would run before the placeholders exist. We poll briefly instead
    // of using a MutationObserver: createIcons() itself mutates the DOM
    // (replacing <i> with <svg>), and an observer reacting to its own
    // mutations risks a feedback loop that pegs the page.
    function ugRenderIcons() {
        if (window.lucide && window.lucide.createIcons) {
            window.lucide.createIcons();
        }
    }
    var ugIconTries = 0;
    var ugIconTimer = setInterval(function() {
        ugRenderIcons();
        ugIconTries++;
        if (ugIconTries >= 20) clearInterval(ugIconTimer);
    }, 500);

    // Auto-scroll the chat to the latest message. Gradio's chatbot scrolls
    // internally via a `.bubble-wrap` div (not the page), so the browser's
    // own "scroll into view on new content" never kicks in — without this,
    // users have to manually drag the scrollbar down after every reply.
    // We watch for DOM changes inside #chat-window (new message bubbles,
    // streamed token updates) and snap scrollTop to the bottom. This is
    // safe from the observer feedback-loop trap that bit the icon code:
    // setting scrollTop doesn't mutate the DOM, so it can't re-trigger
    // the observer.
    var ugScrollTimer = setInterval(function() {
        var wrap = document.querySelector('#chat-window .bubble-wrap');
        if (!wrap) return;
        clearInterval(ugScrollTimer);

        function ugScrollToBottom() {
            wrap.scrollTop = wrap.scrollHeight;
        }
        var ugScrollObserver = new MutationObserver(ugScrollToBottom);
        ugScrollObserver.observe(wrap, { childList: true, subtree: true, characterData: true });
        ugScrollToBottom();
    }, 300);
}
"""

# Loaded into <head> — provides the Lucide icon-rendering script used for
# the topbar, sidebar, and source-badge icons (see SOURCE_ICONS / get_icon_name).
LUCIDE_HEAD = """
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
"""


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

    # Wire interactions
    def respond(message, history):
        if not message.strip():
            return history, ""
        reply = chat(message, history)
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        return history, ""

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