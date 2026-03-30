import faiss
import numpy as np
from .embed import Embedder

class VectorIndex:
    def __init__(self):
        self.embedder = Embedder()
        self.index = None
        self.text_chunks = []

    def build(self, documents):
        """
        documents: list of text chunks
        """
        self.text_chunks = documents

        embeddings = self.embedder.encode(documents)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def search(self, query, top_k=3):
        query_vec = self.embedder.encode([query])
        distances, indices = self.index.search(query_vec, top_k)

        results = [self.text_chunks[i] for i in indices[0]]
        return results