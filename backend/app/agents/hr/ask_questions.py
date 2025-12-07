import json
import os

import faiss
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv

load_dotenv()


EMBED_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"

CHUNKS_DIR = "chunks"
VECTORS_FILE = "vectors.npz"
FAISS_INDEX_FILE = "faiss.index"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)
    return genai


def embed_query(client, query):
    """Use the correct new embedding API."""
    resp = client.embed_content(model=EMBED_MODEL, content=query)
    return np.array(resp["embedding"], dtype="float32")


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

    model = genai.GenerativeModel(LLM_MODEL)
    resp = model.generate_content(prompt)

    print("\nANSWER:\n")
    print(resp.text)
    return resp.text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python ask_question.py "your question here"')
        exit()

    question = " ".join(sys.argv[1:])
    answer_question(question)
