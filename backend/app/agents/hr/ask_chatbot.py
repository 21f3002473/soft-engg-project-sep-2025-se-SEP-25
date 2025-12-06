import os
import json
import pickle
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
import faiss

load_dotenv()

# Config

# Config
LLM_MODEL = "gemini-2.0-flash"
EMBED_MODEL = "gemini-embedding-001"
TOP_K = 5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "data.txt")
VECTOR_STORE_FILE = os.path.join(BASE_DIR, "data", "hr_vectors.pkl")
#LLM_MODEL = "gemini-2.0-flash"
#EMBED_MODEL = "gemini-embedding-001"
#DATA_FILE = "backend/app/agents/hr/data/data.txt"
#VECTOR_STORE_FILE = "backend/app/agents/hr/data/hr_vectors.pkl"
#TOP_K = 5

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai  # return module

def build_vector_store():
    """Embed each line of data.txt using Gemini embeddings and save FAISS index."""
    client = get_client()

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} not found.")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print("Generating embeddings via Gemini...")
    embeddings = []
    for line in lines:
        resp = client.embed_content(model=EMBED_MODEL, content=line)
        emb = np.array(resp["embedding"], dtype="float32")
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product ~ cosine similarity
    index.add(embeddings)

    # Save index and texts
    with open(VECTOR_STORE_FILE, "wb") as f:
        pickle.dump({"index": index, "texts": lines}, f)
    print(f"Vector store saved to {VECTOR_STORE_FILE}")

def load_vector_store():
    if not os.path.exists(VECTOR_STORE_FILE):
        build_vector_store()
    with open(VECTOR_STORE_FILE, "rb") as f:
        data = pickle.load(f)
    return data["index"], data["texts"]

def embed_text(text):
    """Generate embedding for a string using Gemini."""
    client = get_client()
    resp = client.embed_content(model=EMBED_MODEL, content=text)
    emb = np.array(resp["embedding"], dtype="float32").reshape(1, -1)
    faiss.normalize_L2(emb)
    return emb

def retrieve_relevant_chunks(question, top_k=TOP_K):
    """Retrieve top-k relevant lines from HR data using Gemini embeddings and FAISS."""
    index, texts = load_vector_store()
    q_emb = embed_text(question)
    D, I = index.search(q_emb, top_k)
    chunks = [texts[i] for i in I[0]]
    return chunks

def answer_question(question: str):
    try:
        client = get_client()

        # Retrieve top-k relevant lines
        relevant_chunks = retrieve_relevant_chunks(question, top_k=TOP_K)
        if not relevant_chunks:
            return "I don't know"

        context = "\n".join(relevant_chunks)
        prompt = f"""
Use the following HR knowledge base to answer the question concisely.
If the answer is not found in the knowledge base, reply "I don't know".

CONTEXT:
{context}

QUESTION:
{question}
"""

        model = client.GenerativeModel(LLM_MODEL)
        resp = model.generate_content(prompt)
        return resp.text or "I don't know"

    except Exception as e:
        print(f"Error: {e}")
        return "I don't know"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Usage: python ask_chatbot.py "your question here"')
        exit()
    question = " ".join(sys.argv[1:])
    answer = answer_question(question)
    print("\nANSWER:\n")
    print(answer)
