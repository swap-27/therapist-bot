import numpy as np
import faiss
import re

from torch import chunk

def query_search(user_query, index, metadata, embedder, top_k=5):
    query_embeddings = embedder.encode([user_query], show_progress_bar=True, convert_to_numpy=True)
    query_embeddings = query_embeddings.astype(np.float32)
    faiss.normalize_L2(query_embeddings)
    scores, indices = index.search(query_embeddings, k=top_k)
    print("\nTop Results:\n")
    metadata_results = [metadata[idx] for idx in indices[0]]
    for idx, score in enumerate(scores[0]):
        print(f"Result {idx + 1}: Score = {score:.4f}")
        print(f"Metadata: {metadata_results[idx]}")
        print("=" * 80)

    results = []
    for rank, idx in enumerate(indices[0]):
        result = {
            "rank": rank + 1,
            "score": float(scores[0][rank]),
            "category": metadata[idx]["category"],
            "document": metadata[idx]["document"],
            "text": metadata[idx]["text"]
        }
        results.append(result)

    temp_results = [result for result in results if result["score"] > 0.5]  # Filter results based on a score threshold
    if not temp_results:
        print("No results with a score above the threshold. Adding the top result anyway.")
        return results
    return temp_results

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'Page\s+\d+', '', text)
    NOISE_PATTERNS = [
    "Centre for Clinical Interventions",
    "C C I",
    "entre for",
    "linical",
    "nterventions"
    ]
    for pattern in NOISE_PATTERNS:
        text = re.sub(re.escape(pattern), '', text, flags=re.IGNORECASE)
    text = re.sub(
        r"[☐✓▪■□•]",
        "",
        text
    )
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip()
    return text