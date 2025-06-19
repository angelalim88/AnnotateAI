from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGHandler:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            ngram_range=(1,2),
            stop_words=None,  # Keep all words for Indonesian/Betawi
            lowercase=True
        )
        self.vectors = None
        self.knowledge_data = []
    
    def setup_vectorstore(self, knowledge_data):
        """Setup TF-IDF vectorizer dengan knowledge data"""
        self.knowledge_data = knowledge_data
        texts = [item['text'] for item in knowledge_data]
        
        print(f"   Processing {len(texts)} texts...")
        self.vectors = self.vectorizer.fit_transform(texts)
        print(f"   TF-IDF vectorizer ready with {self.vectors.shape[0]} documents, {self.vectors.shape[1]} features")
    
    def find_labels_to_annotate(self, query_text, k=5):
        """Cari label apa saja yang perlu di-annotate berdasarkan TF-IDF similarity"""
        if self.vectors is None:
            return []
        
        # Transform query text ke vector
        query_vector = self.vectorizer.transform([query_text])
        
        # Hitung cosine similarity
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Get top k similar indices dengan threshold
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        labels_to_annotate = []
        similarity_scores = []
        
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score > 0.1:  # threshold similarity
                label = self.knowledge_data[idx]['prodigy_label']
                if label not in labels_to_annotate:
                    labels_to_annotate.append(label)
                    similarity_scores.append(similarity_score)
        
        # Debug info
        if labels_to_annotate:
            print(f"   Found {len(labels_to_annotate)} potential labels:")
            for label, score in zip(labels_to_annotate, similarity_scores):
                print(f"     - {label}: {score:.3f}")
        
        return labels_to_annotate
