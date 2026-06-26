import faiss
import pickle
from config import EMBEDDER as embedder
import numpy as np
from copy import deepcopy
from functions import clean_text

print("Loading FAISS index...")
index = faiss.read_index("vector_store/therapy_index.faiss")
print("FAISS index loaded successfully.")
print("Loading metadata...")
with open("vector_store/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)
print("Metadata loaded successfully.")

def query_search(user_query, top_k=5):
    user_query = clean_text(user_query)
    query_embeddings = embedder.encode([user_query], show_progress_bar=False, convert_to_numpy=True)
    query_embeddings = query_embeddings.astype(np.float32)
    faiss.normalize_L2(query_embeddings)
    scores, indices = index.search(query_embeddings, k=top_k)

    metadata_results = [metadata[idx] for idx in indices[0]]


    results = []
    for rank, idx in enumerate(indices[0]):
        doc = deepcopy(metadata[idx])
        doc.metadata["score"] = float(scores[0][rank])
        doc.metadata["rank"] = rank + 1
        results.append(doc)

    filtered_results = [result for result in results if result.metadata["score"] > 0.5]  # Filter results based on a score threshold
    if not filtered_results:
        return results
    return filtered_results