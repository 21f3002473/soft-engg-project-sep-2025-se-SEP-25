import json
import os
import pickle

import faiss
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "gemini-embedding-001"
TOP_K = 5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "data.txt")
VECTOR_STORE_FILE = os.path.join(BASE_DIR, "data", "hr_vectors.pkl")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai


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

    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

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

        relevant_chunks = retrieve_relevant_chunks(question, top_k=TOP_K)
        if not relevant_chunks:
            prompt = f"""
                You are a helpful and professional HR assistant chatbot.
                If the user greets you (e.g., "hi", "hello", "hey") respond with a friendly greetings only and like profesinally only.

                QUESTION:
                {question}
                
                Use the HR knowledge base *only when it is relevant* to the user’s query and answer professionally like a HR assistant which has already worked in the field.
                And if the user asks something unrelated to HR and also outside the knowledge base, reply politely with:
                "I'm not sure about that, but I can help you with HR-related questions."

                Provide a clear,concise, friendly, and professional answer following the ethics of the working environment.
            """
        else:
            context = "\n".join(relevant_chunks)
            prompt = f"""
                You are a helpful and professional HR assistant chatbot.

                Use the following HR knowledge base *only when it is relevant* to the user’s query.

                If the user greets you (e.g., "hi", "hello", "hey") respond with a friendly greeting.

                If the user asks something unrelated to HR or outside the knowledge base, reply politely with:
                "I'm not sure about that, but I can help you with HR-related questions."

                CONTEXT:
                {context}

                QUESTION:
                {question}

                Provide a clear, friendly, and professional answer.
            """

        model = client.GenerativeModel(LLM_MODEL)
        resp = model.generate_content(prompt)
        return resp.text

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
