from src.loader import load_pdf
from src.chunker import chunk_text
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline


PDF_PATH = "data/sample.pdf"

text, pages = load_pdf(PDF_PATH)
chunks = chunk_text(text)

embedder = EmbeddingModel()
embeddings = embedder.encode_chunks(chunks)

print(f"Pages: {pages}")
print(f"Characters: {len(text)}")
print(f"Total Chunks: {len(chunks)}")
print()
print("Embedding shape:")
print(embeddings.shape)
print()
print("First 10 values of first embedding:")
print(embeddings[0][:10])

for i, chunk in enumerate(chunks[:3]):
    print("=" * 60)
    print(f"Chunk {i+1}")
    print("=" * 60)
    print(chunk)
    print()



store = VectorStore(dimension=384)
store.add_embeddings(embeddings)

query = "Why is self-attention better than RNNs?"
query_embedding = embedder.encode_chunks([query])[0]
distances, indices = store.search(query_embedding, k=5)

print("\nQuestion:")
print(query)

print("\nTop 3 Results:\n")

for i, idx in enumerate(indices):
    print("=" * 60)
    print(f"Rank {i+1}")
    print(f"Chunk Index: {idx}")
    print(f"Distance: {distances[i]:.4f}")
    print()
    print(chunks[idx][:500])
    print()

retrieved_chunks = [chunks[idx] for idx in indices]
rag = RAGPipeline()
answer = rag.generate_answer(query, retrieved_chunks)

print("\n" + "=" * 60)
print("Answer")
print("=" * 60)
print(answer)