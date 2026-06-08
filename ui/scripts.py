"""
Client-side JS and <head> content for the custom Gradio layout.

FILL_INPUT_JS is passed to gr.Blocks(js=...), which Gradio executes as a real
function() {...} on page load — unlike <script> tags injected via gr.HTML(),
which the browser sets via innerHTML and never executes.
"""

# Defining ugFillInput here makes it a real global function the chip
# buttons' inline onclick handlers (built in ui.components.build_chips) can
# call to populate the message textbox.
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
# the topbar, sidebar, and source-badge icons (see ui.components.SOURCE_ICONS
# / get_icon_name).
LUCIDE_HEAD = """
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
"""
