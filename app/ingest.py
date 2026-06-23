import os
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

from app.functions import clean_text

# Embedder initialization
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Constants and variables
PATH  = os.getcwd() + "/data/documents"
METADATA = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
CHUNKED_DOCUMENTS = []

# Getting documents and processing them
print("Ingesting documents from:", PATH)
disorder_folders = os.listdir(PATH)
print("Found disorder folders:", disorder_folders)
# Loop through each disorder folder and process the documents
for disorder in disorder_folders:
    disorder_path = os.path.join(PATH, disorder)
    if os.path.isdir(disorder_path):
        print(f"Processing disorder: {disorder}")
        document_files = os.listdir(disorder_path)
        print(f"Found document files for {disorder}:", document_files)
        # Loop through each document file and extract text
        for doc_file in document_files:
            reader = pypdf.PdfReader(os.path.join(disorder_path, doc_file))
            text = ""
            # Open a text file to write the extracted content
            for page in reader.pages:
                text_temp = page.extract_text()
                if text_temp:  # Check if text was extracted successfully
                    text += text_temp + "\n"  # Append text and a new line for each page
            if len(text.strip()) > 0:
                metadata = {"text": text, "category": disorder, "document": doc_file, "source": os.path.join(disorder_path, doc_file)}
                METADATA.append(metadata)
                print(f"Extracted text from {doc_file} for disorder {disorder}")

for metadata in METADATA:
    chunks = text_splitter.split_text(metadata["text"])
    for chunk in chunks:
        if len(chunk.strip()) < 100:
            continue
        chunk = clean_text(chunk)
        
        CHUNKED_DOCUMENTS.append({"text": chunk, "category": metadata["category"], "document": metadata["document"], "source": metadata["source"]})

print(f"Total chunks created: {len(CHUNKED_DOCUMENTS)}")

chunk_texts = [doc["text"] for doc in CHUNKED_DOCUMENTS]
embeddings = embedder.encode(chunk_texts, show_progress_bar=True, convert_to_numpy=True)

print("Embeddings generated for all chunks.")
print("Embeddings shape:", embeddings.shape)
print(len(METADATA))
print(len(CHUNKED_DOCUMENTS))
print(embeddings.shape)

dimension = embeddings.shape[1]
embeddings = embeddings.astype(np.float32)
faiss.normalize_L2(embeddings)
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
print("Vector store created with FAISS. Total vectors indexed:", index.ntotal)

os.makedirs("vector_store", exist_ok=True)

faiss.write_index(
    index,
    "vector_store/therapy_index.faiss"
)

print("FAISS index saved")

print("Saving metadata...")
with open("vector_store/metadata.pkl", "wb") as f:
    pickle.dump(CHUNKED_DOCUMENTS, f)
print("Metadata saved successfully.")




# QUICK TEST
query = "Why do people seek reassurance?"

query_embedding = embedder.encode(
    [query],
    convert_to_numpy=True
)

distances, indices = index.search(
    query_embedding.astype(np.float32),
    k=5
)

print("\nTop Results:\n")

for idx in indices[0]:

    print("=" * 80)

    print(CHUNKED_DOCUMENTS[idx]["category"])

    print(CHUNKED_DOCUMENTS[idx]["document"])

    print(CHUNKED_DOCUMENTS[idx]["text"][:500])


