import json
import os

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

EMBED_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.0-flash"  # or gemini-2.5-pro

CHUNKS_DIR = "chunks"
VECTORS_FILE = "vectors.npz"
FAISS_INDEX_FILE = "faiss.index"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=api_key)


def embed_query(client, query):
    resp = client.models.embed_content(model=EMBED_MODEL, contents=[query])
    return np.array(resp.embeddings[0].values, dtype="float32")


def load_chunk_text(cid):
    with open(f"{CHUNKS_DIR}/chunk_{cid}.json", "r", encoding="utf-8") as f:
        return json.load(f)["text"]


def answer_question(question, top_k=5):
    client = get_client()

    print("Loading FAISS index...")
    index = faiss.read_index(FAISS_INDEX_FILE)

    vectors = np.load(VECTORS_FILE)["vectors"]

    print("Embedding query...")
    q = embed_query(client, question).reshape(1, -1)
    faiss.normalize_L2(q)

    print("Searching...")
    D, I = index.search(q, top_k)

    contexts = []
    for i, score in zip(I[0], D[0]):
        text = load_chunk_text(int(i))
        contexts.append(f"[chunk {i}, score={score:.4f}]\n{text}")

    final_context = "\n\n".join(contexts)

    prompt = f"""
Use the following context to answer the question.

CONTEXT:
{final_context}

QUESTION:
{question}

Give a concise answer. If not found, say "I don't know".
"""

    print("Generating answer...")
    resp = client.models.generate_content(model=LLM_MODEL, contents=prompt)

    print("\nANSWER:\n")
    print(resp.text)
