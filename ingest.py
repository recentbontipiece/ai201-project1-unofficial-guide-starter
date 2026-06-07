import os
from config import DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_LENGTH


def load_documents():
    """Load all .txt documents from the documents folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            with open(os.path.join(DOCS_PATH, filename), "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({"filename": filename, "content": content})
    print(f"Loaded {len(documents)} document(s) from {DOCS_PATH}")
    return documents


def chunk_document(text, source_filename):
    """
    Split a document into chunks ready for embedding.

    Strategy: paragraph-aware splitting with a character cap and overlap.
      - Paragraphs (split on blank lines) are the natural unit of advice in
        these articles — one paragraph is usually one complete piece of
        advice, so splitting on paragraph boundaries keeps each chunk
        semantically self-contained.
      - chunk_size = 400 characters: long enough to hold a complete piece
        of advice (1-3 sentences), short enough that chunks don't blend
        multiple unrelated tips together.
      - overlap = 80 characters: when a paragraph runs longer than
        chunk_size and has to be split mechanically, the tail of one chunk
        is repeated at the head of the next so advice that spans a forced
        split boundary is still retrievable from either chunk.
      - min_length = 50 characters: filters out whitespace artifacts and
        short fragments (e.g. lone headers) that add noise without useful
        semantic content.

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "source"   : the source filename, e.g. "first_internship_devto.txt" (str)
      - "chunk_id" : a unique identifier, e.g. "first_internship_devto_0" (str)
    """
    prefix = source_filename.replace(".txt", "")
    chunks = []
    counter = 0

    # Split on blank lines so each paragraph is treated as a unit of advice.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    def add_chunk(chunk_text):
        nonlocal counter
        chunk_text = chunk_text.strip()
        if len(chunk_text) >= MIN_CHUNK_LENGTH:
            chunks.append({
                "text": chunk_text,
                "source": source_filename,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

    buffer = ""
    for paragraph in paragraphs:
        # A paragraph that fits within the cap gets grouped with neighbors
        # until adding the next one would exceed chunk_size.
        if len(paragraph) <= CHUNK_SIZE:
            if not buffer:
                buffer = paragraph
            elif len(buffer) + 2 + len(paragraph) <= CHUNK_SIZE:
                buffer = f"{buffer}\n\n{paragraph}"
            else:
                add_chunk(buffer)
                buffer = paragraph
            continue

        # A paragraph longer than chunk_size must be split mechanically
        # using a sliding window with overlap.
        if buffer:
            add_chunk(buffer)
            buffer = ""

        start = 0
        while start < len(paragraph):
            end = start + CHUNK_SIZE
            add_chunk(paragraph[start:end])
            start += CHUNK_SIZE - CHUNK_OVERLAP

    if buffer:
        add_chunk(buffer)

    return chunks


if __name__ == "__main__":
    documents = load_documents()
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc["content"], doc["filename"]))

    print(f"Produced {len(all_chunks)} chunk(s) total")
    print("\n--- Sample chunks ---")
    for chunk in all_chunks[:5]:
        print(f"\n[{chunk['chunk_id']}] ({len(chunk['text'])} chars)")
        print(chunk["text"])
