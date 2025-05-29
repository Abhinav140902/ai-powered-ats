import os
import time
from typing import List, Tuple
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class VectorStore:
    def __init__(self):
        embeddings_start = time.time()
        print("🔍 Loading embeddings model...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = None
        
        embeddings_time = time.time() - embeddings_start
        print(f"✅ Embeddings model loaded in {embeddings_time:.2f}s")
        
    def create_vector_store(self, documents: List[Tuple[str, str]]):
        if not documents:
            raise ValueError("No documents provided")
            
        total_start = time.time()
        print(f"🗃️  Creating vector database from {len(documents)} documents...")
        
        # Document processing timing
        doc_processing_start = time.time()
        langchain_docs = []
        
        for filename, text in documents:
            if text and text.strip() and len(text.strip()) > 10:
                doc = Document(
                    page_content=text[:4000],
                    metadata={"source": filename, "length": len(text)}
                )
                langchain_docs.append(doc)
                print(f"✅ Added {filename}")
        
        doc_processing_time = time.time() - doc_processing_start
        print(f"⏱️  Document processing: {doc_processing_time:.2f}s")
        
        if not langchain_docs:
            raise ValueError("No valid documents")
        
        # Vector generation timing
        vector_start = time.time()
        print("🔄 Generating embeddings...")
        
        self.vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
        
        vector_time = time.time() - vector_start
        print(f"⏱️  Vector generation: {vector_time:.2f}s")
        
        # Save timing
        save_start = time.time()
        try:
            self.vector_store.save_local("data/faiss_index")
            save_time = time.time() - save_start
            print(f"💾 Database saved in {save_time:.2f}s")
        except Exception as e:
            print(f"⚠️  Save error: {e}")
        
        total_time = time.time() - total_start
        print(f"✅ Vector database ready in {total_time:.2f}s total")
        
        # Performance metrics
        docs_per_sec = len(langchain_docs) / total_time
        print(f"📊 Processing rate: {docs_per_sec:.1f} documents/second")
        
        return self.vector_store
    
    def search(self, query: str, k: int = 5):
        """Search method with timing."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        search_start = time.time()
        results = self.vector_store.similarity_search(query, k=k)
        search_time = time.time() - search_start
        
        print(f"⏱️  Vector search: {search_time*1000:.1f}ms for {len(results)} results")
        return results
    
    def as_retriever(self, **kwargs):
        """Return retriever for LangChain."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        return self.vector_store.as_retriever(**kwargs)
