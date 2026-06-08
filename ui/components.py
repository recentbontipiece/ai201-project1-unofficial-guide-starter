"""
HTML fragment builders for the custom Gradio layout.

These render the static chrome around the chatbot — topbar, sidebar, and
example-question chips — as raw HTML strings passed to gr.HTML(). Styling
lives in ui.styles; client-side behavior (icon rendering, chip clicks) lives
in ui.scripts.
"""

import html
import json

from config import SOURCES

EXAMPLE_QUESTIONS = [
    "How do I get a first internship with no experience?",
    "Is LeetCode alone enough for big tech?",
    "What projects actually impress recruiters?",
    "Is a Master's in CS worth it?",
    "How do students handle imposter syndrome?",
    "How do I start contributing to open source?",
]

# Lucide (https://lucide.dev) icon names — rendered client-side via the
# Lucide CDN script (see ui.scripts.LUCIDE_HEAD), replacing
# <i data-lucide="..."> tags with inline outline SVGs. Using a shared icon
# set instead of emoji keeps the sidebar visually consistent across
# platforms/fonts.
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
