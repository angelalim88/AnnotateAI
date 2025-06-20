from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import SIMILARITY_THRESHOLD

class RAGHandler:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            ngram_range=(1,2),
            stop_words=None,
            lowercase=True
        )
        self.vectors = None
        self.knowledge_data = []
    
    def setup_vectorstore(self, knowledge_data):
        self.knowledge_data = knowledge_data
        texts = [item['text'] for item in knowledge_data]
        
        print(f"   Processing {len(texts)} texts...")
        self.vectors = self.vectorizer.fit_transform(texts)
        print(f"   TF-IDF vectorizer ready with {self.vectors.shape[0]} documents, {self.vectors.shape[1]} features")
    
    def find_labels_to_annotate(self, query_text, k=3):
        if self.vectors is None:
            return []
        
        query_vector = self.vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        labels_to_annotate = []
        similarity_scores = []
        
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score > SIMILARITY_THRESHOLD:
                label = self.knowledge_data[idx]['prodigy_label']
                if label not in labels_to_annotate:
                    labels_to_annotate.append(label)
                    similarity_scores.append(similarity_score)
        
        if labels_to_annotate:
            print(f"   Found {len(labels_to_annotate)} potential labels:")
            for label, score in zip(labels_to_annotate, similarity_scores):
                print(f"     - {label}: {score:.3f}")
        
        return labels_to_annotate
