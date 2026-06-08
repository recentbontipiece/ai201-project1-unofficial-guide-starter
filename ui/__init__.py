"""
View layer for The Unofficial Guide.

Everything Gradio renders to the browser — HTML fragments, CSS, and
client-side JS — lives in this package, decoupled from app.py (which wires
that view to the retrieval/generation business logic in retriever.py and
generator.py). This mirrors the View / View-glue split familiar from
MVVM-style architectures: app.py is the thin controller that connects user
events to the model layer; this package owns everything about how the page
looks and behaves in the browser.
"""

from ui.components import (
    EXAMPLE_QUESTIONS,
    build_chips,
    build_sidebar,
    build_topbar,
)
from ui.scripts import FILL_INPUT_JS, LUCIDE_HEAD
from ui.styles import CUSTOM_CSS

__all__ = [
    "EXAMPLE_QUESTIONS",
    "build_chips",
    "build_sidebar",
    "build_topbar",
    "FILL_INPUT_JS",
    "LUCIDE_HEAD",
    "CUSTOM_CSS",
]
