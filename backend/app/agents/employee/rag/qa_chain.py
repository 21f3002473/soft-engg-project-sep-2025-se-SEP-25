import os
import pickle

from .gemini_llm import GeminiLLM

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
STATIC_DIR = os.path.join(project_root, "static", "employee")
VECTORSTORE_PATH = os.path.join(STATIC_DIR, "vectorstore.pkl")


def load_vector_store():
    """Loads the saved FAISS vector store from disk."""

    if not os.path.exists(VECTORSTORE_PATH):
        raise FileNotFoundError(
            f"[RAG ERROR] vectorstore.pkl not found at:\n{VECTORSTORE_PATH}\n"
            "Run build_vector_store.py first."
        )

    with open(VECTORSTORE_PATH, "rb") as f:
        return pickle.load(f)


def create_rag_components():
    """
    Loads:
      - FAISS Vector Store (for retrieval)
      - Gemini LLM wrapper (for generation)

    Returns:
      retriever, llm
    """

    vectorstore = load_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = GeminiLLM()

    return retriever, llm


def get_rag_answer(user_question: str, employee_context: str):
    """
    Main RAG function that:
    1. Retrieves relevant HR chunks
    2. Builds a combined prompt
    3. Calls Gemini to produce answer
    """

    retriever, llm = create_rag_components()

    docs = retriever.invoke(user_question)
    context_text = (
        "\n\n".join([d.page_content for d in docs]) or "No relevant info found."
    )

    prompt = f"""
You are Sync'em HR AI Assistant.

USER CONTEXT:
{employee_context}

GLOBAL HR CONTEXT:
{context_text}

QUESTION:
{user_question}

Guidelines:
- Prefer USER CONTEXT if the question is personal.
- Prefer GLOBAL CONTEXT for HR policies, rules, benefits, and processes.
- If the info does not exist in GLOBAL CONTEXT, say you don’t know.
- Do NOT hallucinate new HR rules.
"""

    answer = llm.invoke(prompt)
    return answer
