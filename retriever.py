import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.

    _collection.add() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface which source document a result
                    came from (used for citations in generate_response())
      - ids       : the unique chunk_id strings used to identify each entry

    You don't generate embeddings manually here — you hand over the text
    and ChromaDB handles the vector math.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant chunks for a user's question.

    Runs a semantic search via _collection.query(), which embeds the query
    with the same model used at ingestion time and returns the closest
    chunks by cosine distance (lower = more similar).

    _collection.query() returns nested lists — one list per query string.
    Since we only ever pass one query, we index into [0] to get the actual
    results for that query.

    Returns a list of dicts ordered from most to least relevant, each with:
      - "text"     : the chunk text
      - "source"   : the source filename this chunk came from (for citations)
      - "distance" : cosine distance score (lower = more similar)

    Returns an empty list if the collection has no documents yet.
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


if __name__ == "__main__":
    # Quick smoke test: run a few of the evaluation questions from planning.md
    # and print the retrieved chunks so you can eyeball relevance and distance.
    test_queries = [
        "What do students recommend for getting a first software internship with no experience?",
        "Is practicing LeetCode alone enough to pass technical interviews at big tech companies?",
        "Is a Master's degree in Computer Science worth pursuing for a software engineering career?",
    ]

    for q in test_queries:
        print(f"\n=== Query: {q}")
        for r in retrieve(q):
            preview = r["text"][:120].replace("\n", " ")
            print(f"  [{r['source']}] (distance={r['distance']:.3f}) {preview}...")
