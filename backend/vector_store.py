import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalVectorStore:
    def __init__(self, filepath="models/vector_index.pkl"):
        # Put models folder relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, filepath)
        self.documents = []  # List of dicts: {"id": int, "text": str, "metadata": dict}
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectors = None  # Sparse matrix representation of document vectors

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        joblib.dump({
            "documents": self.documents,
            "vectorizer": self.vectorizer,
            "vectors": self.vectors
        }, self.filepath)
        print(f"Saved vector index with {len(self.documents)} items to {self.filepath}")

    def load(self) -> bool:
        if os.path.exists(self.filepath):
            try:
                data = joblib.load(self.filepath)
                self.documents = data.get("documents", [])
                self.vectorizer = data.get("vectorizer", TfidfVectorizer(stop_words='english'))
                self.vectors = data.get("vectors", None)
                print(f"Loaded vector index with {len(self.documents)} items.")
                return True
            except Exception as e:
                print(f"Error loading vector index: {e}")
        return False

    def rebuild_index(self, tickets):
        """
        Rebuilds the vector index from scratch using a list of ORM database tickets.
        """
        self.documents = []
        for ticket in tickets:
            self.documents.append({
                "id": ticket.id,
                "text": ticket.raw_text,
                "metadata": {
                    "category": ticket.category,
                    "feedback_type": ticket.feedback_type,
                    "urgency_score": ticket.urgency_score,
                    "status": ticket.status
                }
            })
        
        if not self.documents:
            self.vectors = None
            return

        texts = [doc["text"] for doc in self.documents]
        self.vectors = self.vectorizer.fit_transform(texts)
        self.save()

    def add_document(self, doc_id, text, metadata):
        """
        Adds a single new document dynamically and refits the TF-IDF space.
        """
        # Ensure no duplicates
        if any(doc["id"] == doc_id for doc in self.documents):
            return
            
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata
        })
        
        texts = [doc["text"] for doc in self.documents]
        self.vectors = self.vectorizer.fit_transform(texts)
        self.save()

    def search(self, query: str, top_k: int = 3):
        """
        Calculates cosine similarities and returns top_k matching documents with scores.
        """
        if not self.documents or self.vectors is None:
            return []

        try:
            # Transform search query to sparse vector
            query_vector = self.vectorizer.transform([query])
        except Exception as e:
            print(f"Error vectorizing search query: {e}")
            return []

        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        
        # Sort scores in descending order and slice
        top_indexes = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indexes:
            score = float(similarities[idx])
            # Return matches with positive similarity scores
            results.append({
                "document": self.documents[idx],
                "score": score
            })
        return results
