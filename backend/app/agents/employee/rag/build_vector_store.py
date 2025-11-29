import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from data_loader import load_data


def build_faiss_index():
    """Builds a FAISS index from HR policies & course data."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

    static_dir = os.path.join(project_root, "static", "employee")
    data_path = os.path.join(static_dir, "data.txt")
    index_path = os.path.join(static_dir, "vectorstore.pkl")

    print(f"[INFO] Loading HR policy data from: {data_path}")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"[ERROR] data.txt not found at: {data_path}")

    docs = load_data(data_path)
    print(f"[INFO] Loaded {len(docs)} text chunks.")

    print("[INFO] Creating embeddings with MiniLM-L6-v2 ...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("[INFO] Building FAISS vector store ...")
    vector_store = FAISS.from_documents(docs, embeddings)

    print(f"[INFO] Saving FAISS index {index_path}")

    with open(index_path, "wb") as f:
        pickle.dump(vector_store, f)

    print("[SUCCESS] Vector store successfully saved!")
    print(f"[SUCCESS] Location: {index_path}")


if __name__ == "__main__":
    build_faiss_index()
