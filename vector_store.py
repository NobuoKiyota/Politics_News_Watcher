import chromadb
import google.generativeai as genai
import config
import os
from chromadb.utils import embedding_functions

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        # text-embedding-004
        # Chroma expects list of list of floats
        results = []
        for text in input:
            try:
                emb = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )['embedding']
                # Ensure it's a list of floats
                results.append(list(emb))
            except Exception as e:
                print(f"Embedding error for '{text[:10]}...': {e}")
                # Return empty list or zeros? Chroma might crash.
                # Better to return None and handle? But type signature matches.
                # Let's return a dummy vector or reraise.
                raise e
        return results

class NewsVectorStore:
    def __init__(self):
        # Persistent storage
        self.persist_path = os.path.join(config.DATA_DIR, 'chroma_db')
        self.client = chromadb.PersistentClient(path=self.persist_path)
        
        self.embedding_fn = GeminiEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="politics_news",
            embedding_function=self.embedding_fn
        )

    def is_duplicate(self, text, threshold=0.3):
        """
        Check if semantically similar text exists.
        Threshold: 
        Cosine Distance = 1 - Cosine Similarity.
        If threshold is 0.3, it means Similarity > 0.7.
        """
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=1
            )
            
            if not results['distances'] or not results['distances'][0]:
                return False
                
            distance = results['distances'][0][0]
            # print(f"Distance: {distance}")
            
            return distance < threshold
        except Exception as e:
            print(f"Vector Query Error: {e}")
            return False

    def is_duplicate_id(self, article_id):
        """
        Check if an article ID already exists.
        """
        try:
            results = self.collection.get(ids=[article_id])
            # results['ids'] is a list of found IDs
            if results and results['ids']:
                return True
            return False
        except Exception as e:
            print(f"Vector ID Check Error: {e}")
            return False

    def add_article(self, article_id, text, metadata):
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[article_id]
        )

if __name__ == "__main__":
    # Final Verification
    store = NewsVectorStore()
    text1 = "岸田首相は新しい経済対策を発表しました。"
    text2 = "本日、政府は新たな経済支援策を打ち出しました。"
    text3 = "今日の天気は晴れです。" 
    
    # Clean DB for test? No, Persistent. 
    # Just check query.
    # Note: If reusing ID, add might fail or update? Chroma updates if ID exists.
    try:
        store.add_article("id1", text1, {"source": "test"})
        
        d1 = store.is_duplicate(text2, threshold=0.4)
        d2 = store.is_duplicate(text3, threshold=0.4)
        
        print(f"Duplicate(Semantic): {d1}")
        print(f"Duplicate(Unrelated): {d2}")
    except Exception as e:
        print(e)
