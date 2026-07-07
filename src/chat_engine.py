from src.loader import load_pdf
from src.chunker import chunk_text
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline


class ChatEngine:

    def __init__(self, max_history_turns=4):

        self.embedder = EmbeddingModel()
        self.rag = RAGPipeline()

        self.chunks = None
        self.store = None

        self.history = []  # list of (question, answer) tuples
        self.max_history_turns = max_history_turns

    def load_document(self, pdf_path):

        text, pages = load_pdf(pdf_path)
        self.chunks = chunk_text(text)
        embeddings = self.embedder.encode_chunks(self.chunks)
        self.store = VectorStore(dimension=384)
        self.store.add_embeddings(embeddings)
        self.history = []  # reset memory when a new document is loaded
        return pages

    def ask(self, question):

        query_embedding = self.embedder.encode_chunks([question])[0]
        distances, indices = self.store.search(query_embedding, k=5)
        retrieved_chunks = [self.chunks[idx] for idx in indices]

        recent_history = self.history[-self.max_history_turns:]
        answer = self.rag.generate_answer(question, retrieved_chunks, history=recent_history)

        self.history.append((question, answer))

        return answer