import os
import hashlib
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer


class LongTermMemory:

    def __init__(self):
        """
        Connects to Pinecone and loads the embedding model.
        Uses sentence-transformers locally for embeddings — completely free,
        no API calls needed for generating embeddings.
        """
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY is not set in your .env file")

        self.index_name = os.getenv("PINECONE_INDEX", "ai-secretary")
        self.pc = Pinecone(api_key=api_key)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384  # dimension for all-MiniLM-L6-v2

        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        """
        Creates the Pinecone index if it doesn't exist yet.
        """
        existing = [i.name for i in self.pc.list_indexes()]
        if self.index_name not in existing:
            print(f"[LongTermMemory] Creating Pinecone index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"[LongTermMemory] Index created successfully.")

    def _embed(self, text: str) -> List[float]:
        """
        Converts text into a vector embedding using local model.
        """
        return self.model.encode(text).tolist()

    def _generate_id(self, text: str) -> str:
        """
        Generates a unique ID for a memory entry based on its content.
        """
        return hashlib.md5(text.encode()).hexdigest()

    def save(self, text: str, metadata: Dict[str, Any] = {}):
        """
        Embeds and stores a piece of text in Pinecone.
        metadata can include things like type, date, source.
        Example:
            memory.save(
                "User prefers morning meetings",
                {"type": "preference", "source": "conversation"}
            )
        """
        vector = self._embed(text)
        doc_id = self._generate_id(text)

        metadata["text"] = text

        self.index.upsert(vectors=[{
            "id": doc_id,
            "values": vector,
            "metadata": metadata
        }])
        print(f"[LongTermMemory] Saved: '{text[:60]}...' " if len(text) > 60 else f"[LongTermMemory] Saved: '{text}'")

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Searches Pinecone for the most semantically similar memories.
        Returns top_k results with their text and metadata.
        Example:
            results = memory.recall("does the user prefer morning or evening?")
        """
        vector = self._embed(query)
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )

        matches = []
        for match in results.matches:
            matches.append({
                "text": match.metadata.get("text", ""),
                "score": round(match.score, 4),
                "metadata": match.metadata
            })
        return matches

    def delete(self, text: str):
        """
        Deletes a specific memory by its content.
        """
        doc_id = self._generate_id(text)
        self.index.delete(ids=[doc_id])
        print(f"[LongTermMemory] Deleted memory: '{text}'")