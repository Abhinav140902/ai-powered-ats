from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import requests
import time
import json
import os

class QueryEngine:
    def __init__(self, vector_store_wrapper):
        """Initialize with VectorStore wrapper object."""
        init_start = time.time()
        self.vector_store_wrapper = vector_store_wrapper
        
        print("🤖 Setting up Llama2 7B AI model...")
        
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Time the model setup
        setup_start = time.time()
        self._setup_ollama_model(ollama_base_url)
        setup_time = time.time() - setup_start
        print(f"⏱️  Model setup: {setup_time:.2f}s")
        
        # Time the LLM initialization
        llm_start = time.time()
        self.llm = Ollama(
            model="llama2:7b",
            base_url=ollama_base_url,
            temperature=0.2,
        )
        llm_time = time.time() - llm_start
        print(f"⏱️  LLM initialization: {llm_time:.2f}s")
        
        total_init_time = time.time() - init_start
        print(f"✅ Llama2 7B ready in {total_init_time:.2f}s total!")
        
    def _setup_ollama_model(self, base_url):
        connection_start = time.time()
        print("⏳ Connecting to Ollama...")
        
        # Wait for service
        for i in range(30):
            try:
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    connection_time = time.time() - connection_start
                    print(f"✅ Ollama connected in {connection_time:.2f}s")
                    break
            except:
                if i < 29:
                    print(f"⏳ Waiting... ({i+1}/30)")
                    time.sleep(3)
                else:
                    raise Exception("❌ Could not connect to Ollama")
        
        # Check/download model
        try:
            model_check_start = time.time()
            models_response = requests.get(f"{base_url}/api/tags")
            models = models_response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            llama2_available = any("llama2" in name.lower() for name in model_names)
            
            if not llama2_available:
                print("📥 Downloading Llama2 7B...")
                print("💡 This takes 5-15 minutes (one-time)")
                
                download_start = time.time()
                pull_response = requests.post(
                    f"{base_url}/api/pull",
                    json={"name": "llama2:7b"},
                    stream=True,
                    timeout=1800
                )
                
                if pull_response.status_code == 200:
                    for line in pull_response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "status" in data:
                                    print(f"📥 {data['status']}")
                            except:
                                pass
                    
                    download_time = time.time() - download_start
                    print(f"✅ Download complete in {download_time/60:.1f} minutes!")
            else:
                model_check_time = time.time() - model_check_start
                print(f"✅ Llama2 ready (checked in {model_check_time:.2f}s)")
                
        except Exception as e:
            print(f"⚠️  Model setup warning: {e}")
    
    def find_matching_resumes(self, job_description: str, top_k: int = 5):
        """Find matching resumes with timing."""
        if not job_description.strip():
            return []
            
        search_start = time.time()
        print(f"🔍 Searching for top {top_k} matching resumes...")
        
        try:
            results = self.vector_store_wrapper.search(job_description, k=top_k)
            search_time = time.time() - search_start
            
            print(f"✅ Found {len(results)} matching resumes")
            print(f"⏱️  Total search time: {search_time:.3f}s")
            
            if len(results) > 0:
                print(f"📊 Search efficiency: {len(results)/search_time:.1f} results/second")
            
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def setup_natural_language_query(self):
        """Setup Q&A chain with timing."""
        setup_start = time.time()
        print("🔗 Setting up Q&A system...")
        
        try:
            retriever_start = time.time()
            retriever = self.vector_store_wrapper.as_retriever(search_kwargs={"k": 3})
            retriever_time = time.time() - retriever_start
            print(f"⏱️  Retriever setup: {retriever_time:.3f}s")
            
            chain_start = time.time()
            prompt = PromptTemplate.from_template("""
You are an HR assistant. Answer based only on the resume information provided.

Resume Information:
{context}

Question: {input}

Answer clearly and concisely. If information is not available, say "I don't have that information."

Answer: """)
            
            document_chain = create_stuff_documents_chain(self.llm, prompt)
            self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            chain_time = time.time() - chain_start
            print(f"⏱️  Chain setup: {chain_time:.3f}s")
            
            total_setup_time = time.time() - setup_start
            print(f"✅ Q&A system ready in {total_setup_time:.3f}s")
            
        except Exception as e:
            print(f"❌ Q&A setup failed: {e}")
            self.retrieval_chain = None
        
    def query(self, question: str):
        """Answer questions with detailed timing."""
        if not question.strip():
            return "Please ask a specific question."
            
        query_start = time.time()
        
        # Setup timing
        if not hasattr(self, 'retrieval_chain') or self.retrieval_chain is None:
            setup_start = time.time()
            self.setup_natural_language_query()
            setup_time = time.time() - setup_start
            print(f"⏱️  Q&A setup time: {setup_time:.3f}s")
        
        if not self.retrieval_chain:
            return "Q&A system not available."
        
        print("🤖 Llama2 is thinking...")
        thinking_start = time.time()
        
        try:
            # Document retrieval timing
            retrieval_start = time.time()
            response = self.retrieval_chain.invoke({"input": question})
            total_response_time = time.time() - thinking_start
            
            answer = response.get("answer", "").strip()
            
            if not answer:
                return "I couldn't generate an answer. Please try rephrasing."
            
            # Performance metrics
            query_total_time = time.time() - query_start
            print(f"⏱️  AI thinking time: {total_response_time:.2f}s")
            print(f"⏱️  Total query time: {query_total_time:.2f}s")
            
            # Estimate tokens per second (rough calculation)
            answer_length = len(answer.split())
            if total_response_time > 0:
                tokens_per_sec = answer_length / total_response_time
                print(f"📊 Generation speed: ~{tokens_per_sec:.1f} tokens/second")
            
            return answer
            
        except Exception as e:
            error_time = time.time() - query_start
            print(f"❌ Query error after {error_time:.2f}s: {e}")
            return f"Sorry, there was an error: {str(e)}"
