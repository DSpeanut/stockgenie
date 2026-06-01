import chromadb

from config.settings import VECDB_PATH


def get_chroma_client():
    return chromadb.PersistentClient(path=VECDB_PATH)
