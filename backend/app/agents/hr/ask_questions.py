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
    return resp.text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python ask_question.py "your question here"')
        exit()

    question = " ".join(sys.argv[1:])
    answer_question(question)


'''
import json
import os
from pathlib import Path

import faiss
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

EMBED_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.0-flash"  # or gemini-2.5-pro

PDF_FILE = "app/agents/hr/docs/Human Resources Policy.pdf"
CHUNKS_DIR = "chunks"
VECTORS_FILE = "vectors.npz"
FAISS_INDEX_FILE = "faiss.index"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=api_key)


def embed_texts(client, texts):
    vectors = []
    for t in texts:
        resp = client.models.embed_content(model=EMBED_MODEL, contents=[t])
        vectors.append(np.array(resp.embeddings[0].values, dtype="float32"))
    vectors = np.vstack(vectors)
    faiss.normalize_L2(vectors)
    return vectors


def preprocess_pdf():
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    reader = PdfReader(PDF_FILE)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Split into chunks
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]
        chunks.append(chunk_text)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    # Save chunks as JSON
    for i, chunk in enumerate(chunks):
        with open(f"{CHUNKS_DIR}/chunk_{i}.json", "w", encoding="utf-8") as f:
            json.dump({"text": chunk}, f, ensure_ascii=False)

    return chunks


def load_chunk_text(cid):
    with open(f"{CHUNKS_DIR}/chunk_{cid}.json", "r", encoding="utf-8") as f:
        return json.load(f)["text"]


def build_index_if_missing(client):
    if Path(FAISS_INDEX_FILE).exists() and Path(VECTORS_FILE).exists():
        print("FAISS index already exists, loading...")
        vectors = np.load(VECTORS_FILE)["vectors"]
        index = faiss.read_index(FAISS_INDEX_FILE)
    else:
        print("Preprocessing PDF and building FAISS index...")
        chunks = preprocess_pdf()
        vectors = embed_texts(client, chunks)

        # Save vectors
        np.savez(VECTORS_FILE, vectors=vectors)

        # Build FAISS index
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, FAISS_INDEX_FILE)
        print("FAISS index and vectors saved.")
    return index, vectors


def embed_query(client, query):
    resp = client.models.embed_content(model=EMBED_MODEL, contents=[query])
    return np.array(resp.embeddings[0].values, dtype="float32")


def answer_question(question, top_k=5):
    client = get_client()
    index, vectors = build_index_if_missing(client)

    # Embed query
    q = embed_query(client, question).reshape(1, -1)
    faiss.normalize_L2(q)

    # Search
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

    resp = client.models.generate_content(model=LLM_MODEL, contents=prompt)
    return resp.text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python ask_questions.py "your question here"')
        exit()

    question = " ".join(sys.argv[1:])
    answer_question(question)
'''
'''
import json
import os
from pathlib import Path

import faiss
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

EMBED_MODEL = "text-embedding-004"   # latest recommended model
LLM_MODEL = "gemini-2.0-flash"       # or gemini-2.5-pro

PDF_FILE = "app/agents/hr/docs/Human Resources Policy.pdf"
CHUNKS_DIR = "chunks"
VECTORS_FILE = "vectors.npz"
FAISS_INDEX_FILE = "faiss.index"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


# -------------------------
# INIT CLIENT
# -------------------------
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)
    return genai   # return module, not Client()


# -------------------------
# EMBEDDING FUNCTIONS
# -------------------------
def embed_texts(client, texts):
    vectors = []
    for t in texts:
        resp = client.embed_content(model=EMBED_MODEL, content=t)
        vectors.append(np.array(resp["embedding"], dtype="float32"))

    vectors = np.vstack(vectors)
    faiss.normalize_L2(vectors)
    return vectors


def embed_query(client, query):
    resp = client.embed_content(model=EMBED_MODEL, content=query)
    return np.array(resp["embedding"], dtype="float32")


# -------------------------
# PDF PROCESSING + CHUNKING
# -------------------------
def preprocess_pdf():
    os.makedirs(CHUNKS_DIR, exist_ok=True)

    reader = PdfReader(PDF_FILE)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    # save each chunk
    for i, chunk in enumerate(chunks):
        with open(f"{CHUNKS_DIR}/chunk_{i}.json", "w", encoding="utf-8") as f:
            json.dump({"text": chunk}, f, ensure_ascii=False)

    return chunks


def load_chunk_text(cid):
    with open(f"{CHUNKS_DIR}/chunk_{cid}.json", "r", encoding="utf-8") as f:
        return json.load(f)["text"]


# -------------------------
# BUILD / LOAD FAISS INDEX
# -------------------------
def build_index_if_missing(client):
    if Path(FAISS_INDEX_FILE).exists() and Path(VECTORS_FILE).exists():
        vectors = np.load(VECTORS_FILE)["vectors"]
        index = faiss.read_index(FAISS_INDEX_FILE)
    else:
        chunks = preprocess_pdf()
        vectors = embed_texts(client, chunks)

        # save vectors
        np.savez(VECTORS_FILE, vectors=vectors)

        # build FAISS index
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, FAISS_INDEX_FILE)

    return index, vectors


# -------------------------
# ANSWER QUESTION
# -------------------------
def answer_question(question, top_k=5):
    client = get_client()
    index, vectors = build_index_if_missing(client)

    q = embed_query(client, question).reshape(1, -1)
    faiss.normalize_L2(q)

    D, I = index.search(q, top_k)

    # collect context
    contexts = []
    for i, score in zip(I[0], D[0]):
        text = load_chunk_text(int(i))
        contexts.append(f"[chunk {i} | score={score:.4f}]\n{text}")

    final_context = "\n\n".join(contexts)

    prompt = f"""
Use the context below to answer the question.

CONTEXT:
{final_context}

QUESTION:
{question}

If the answer is not in the context, respond: "I don't know".
"""

    model = client.GenerativeModel(LLM_MODEL)
    resp = model.generate_content(prompt)

    return resp.text


# -------------------------
# CLI USAGE
# -------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python ask_questions.py "your question here"')
        exit()

    question = " ".join(sys.argv[1:])
    print(answer_question(question))
'''
