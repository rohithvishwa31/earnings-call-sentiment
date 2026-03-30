from .index import VectorIndex

class Retriever:
    def __init__(self):
        self.index = VectorIndex()

    def fit(self, text_chunks):
        self.index.build(text_chunks)

    def query(self, query_text, top_k=3):
        return self.index.search(query_text, top_k)