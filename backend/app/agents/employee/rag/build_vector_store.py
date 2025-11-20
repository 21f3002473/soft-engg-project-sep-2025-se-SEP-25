import pickle

from data_loader import load_schemes_data
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS


def build_faiss_index():
    """Builds a FAISS index from the schemes data and saves it to a file."""
    docs = load_schemes_data()
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_documents(docs, embeddings)

    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vector_store, f)
    print("FAISS index built and saved as 'vectorstore.pkl'.")


if __name__ == "__main__":
    build_faiss_index()
