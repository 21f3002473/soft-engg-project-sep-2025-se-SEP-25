from typing_extensions import Self
from langchain_community.vectorstores.chroma import Chroma
from threading import Lock
from chromadb import Client
from chromadb.config import Settings


class ChromaVectorStore(Chroma):
    """Chroma Vector Store Wrapper for PM Requirements Agent."""

    #  singleton pattern could be applied here if needed in future
    _instance = None
    _lock = Lock()

    def __new__(cls, persist_directory="chroma_store"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)

                    # Initialize the client
                    cls._instance.client = Client(
                        Settings(
                            chroma_db_impl="duckdb+parquet",
                            persist_directory=persist_directory,  # folder for persistence
                        )
                    )
        return cls._instance

    def get_client(self):
        return self.client
