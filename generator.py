from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, SOURCE_BY_FILENAME

_client = Groq(api_key=GROQ_API_KEY)

FALLBACK_NO_CHUNKS = (
    "I couldn't find anything relevant in the loaded documents. "
    "Try rephrasing your question — or check that your ingestion pipeline is working."
)

# Exact fallback line from planning.md > Retrieval Approach > Grounding
# instruction. Used to detect when the model declined to answer so we can
# skip attaching a "Sources" section that would otherwise look like it
# backs an answer that was never actually given.
FALLBACK_NOT_IN_CONTEXT = "I don't have enough information in my sources to answer that."

# Exact grounding instruction from planning.md > Retrieval Approach.
# This is the single most important line in the system — it's what stops
# the model from answering out of its own training knowledge.
SYSTEM_PROMPT = (
    "You are an assistant that answers questions about CS student career advice "
    "using ONLY the context provided below. Do not use any outside knowledge.\n\n"
    "If the context does not contain enough information to answer the question, "
    f"respond exactly with: \"{FALLBACK_NOT_IN_CONTEXT}\"\n\n"
    "When you do answer, base your response strictly on the provided context and "
    "do not speculate beyond it. Write your answer as plain prose only: do not "
    "cite filenames, source labels, or bracketed reference numbers like [1] "
    "inline, and do not add your own \"Sources\" section, list, or footer — "
    "a sources list is appended automatically after your answer, so adding "
    "one yourself would create a duplicate."
)


def _format_context(retrieved_chunks):
    """
    Build a context block from retrieved chunks, with no source labels at all.

    Earlier versions labeled each chunk with its filename (e.g. "(source:
    job_market_prep_hn.txt)") or an index (e.g. "[1]"), but the model mimicked
    those labels verbatim in its prose — first leaking raw filenames, then
    inventing a bogus "[1] [2] [3]" references list once the labels became
    bracketed numbers. Plain, unlabeled chunks give it nothing to echo.
    Source attribution is handled entirely by the programmatic "Sources:"
    section appended in generate_response.
    """
    return "\n\n".join(chunk["text"] for chunk in retrieved_chunks)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "source"   : the source filename
      - "distance" : cosine distance score (lower = more similar)

    Grounding is enforced two ways:
      1. The system prompt instructs the model to answer only from the
         provided context and gives it an exact fallback line to use when
         the context is insufficient (see SYSTEM_PROMPT above).
      2. Source attribution is NOT left to the model — we append the list
         of retrieved source filenames after generation, so citations are
         guaranteed to be present and accurate regardless of what the model
         chooses to mention in its prose.

    Returns the response as a plain string containing the answer followed
    by a "Sources:" section listing the documents the context was drawn from.
    """
    if not retrieved_chunks:
        return FALLBACK_NO_CHUNKS

    context = _format_context(retrieved_chunks)
    user_message = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer the question using only the context above."
    )

    completion = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    answer = completion.choices[0].message.content.strip()

    # If the model declined to answer (the retrieved chunks were too weak
    # to be useful), don't attach a Sources list — those chunks didn't
    # actually back any answer, so citing them would be misleading.
    if answer == FALLBACK_NOT_IN_CONTEXT:
        return answer

    # Source attribution is appended programmatically — guaranteed present,
    # not dependent on the model choosing to cite correctly on its own.
    # We cite the original public article (display name + URL), not the
    # private local .txt working copy, since that's the actual reference
    # a reader could go verify the answer against.
    filenames = sorted({chunk["source"] for chunk in retrieved_chunks})
    sources_block = "\n".join(
        f"- [{SOURCE_BY_FILENAME[f]['display_name']}]({SOURCE_BY_FILENAME[f]['url']})"
        for f in filenames
    )

    return f"{answer}\n\nSources:\n{sources_block}"
