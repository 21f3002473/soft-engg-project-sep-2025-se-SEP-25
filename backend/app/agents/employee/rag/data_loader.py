import os

from langchain_community.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "],
    )

    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_path = os.path.join(project_root, "static", "employee", "data.txt")

    docs = load_data(data_path)
    print(f"Loaded {len(docs)} document chunks from RAG dataset.")
