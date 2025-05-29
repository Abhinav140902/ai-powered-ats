import os
import time
from datetime import datetime
from resume_processor import ResumeProcessor
from vector_store import VectorStore  
from query_engine import QueryEngine

def print_banner():
    print("\n" + "="*60)
    print("🎯 AI-Powered ATS - FREE Llama2 7B Edition")
    print("🚀 No API costs • Complete privacy • Local AI")
    print("🧠 Powered by Llama2 7B (3.8GB model)")
    print("="*60)

def print_section(title):
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print("="*50)

def format_time(seconds):
    """Format time in a readable way."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"

def main():
    total_start_time = time.time()
    print_banner()
    
    # Performance tracking
    performance_stats = {
        'resume_processing': 0,
        'vector_store_creation': 0,
        'ai_model_setup': 0,
        'job_matching': 0,
        'total_queries': 0,
        'total_query_time': 0,
        'average_query_time': 0
    }
    
    try:
        # STEP 1: Resume Processing
        print_section("STEP 1: RESUME PROCESSING")
        step1_start = time.time()
        
        processor = ResumeProcessor()
        
        print("📁 Loading resumes...")
        resumes = processor.load_resumes()
        
        if not resumes:
            print("❌ No resumes found in data/resumes/")
            return
        
        print(f"✅ Loaded {len(resumes)} resumes")
        for filename, _ in resumes:
            print(f"   📄 {filename}")
        
        print("🧹 Processing resume text...")
        
        cleaned_resumes = []
        for filename, text in resumes:
            text_start = time.time()
            cleaned_text = processor.clean_text(text)
            text_time = time.time() - text_start
            
            if cleaned_text and len(cleaned_text.strip()) > 50:
                cleaned_resumes.append((filename, cleaned_text))
                print(f"✅ Processed: {filename} ({len(cleaned_text)} chars) - {format_time(text_time)}")
        
        if not cleaned_resumes:
            print("❌ No valid resumes after processing")
            return
        
        step1_time = time.time() - step1_start
        performance_stats['resume_processing'] = step1_time
        print(f"⏱️  Step 1 completed in: {format_time(step1_time)}")
        
        # STEP 2: Vector Store Creation
        print_section("STEP 2: BUILDING SEARCH DATABASE")
        step2_start = time.time()
        
        vector_store = VectorStore()
        vector_store.create_vector_store(cleaned_resumes)
        
        step2_time = time.time() - step2_start
        performance_stats['vector_store_creation'] = step2_time
        print(f"⏱️  Step 2 completed in: {format_time(step2_time)}")
        
        # STEP 3: AI System Setup
        print_section("STEP 3: STARTING AI SYSTEM")
        step3_start = time.time()
        
        query_engine = QueryEngine(vector_store)
        
        step3_time = time.time() - step3_start
        performance_stats['ai_model_setup'] = step3_time
        print(f"⏱️  Step 3 completed in: {format_time(step3_time)}")
        
        # STEP 4: Job Matching
        print_section("STEP 4: JOB MATCHING")
        print("📝 Enter job description (Ctrl+D when done):")
        print("-" * 50)
        
        job_lines = []
        try:
            while True:
                job_lines.append(input())
        except EOFError:
            job_description = '\n'.join(job_lines).strip()
        
        if not job_description:
            print("❌ No job description provided")
            return
        
        print(f"\n📊 Job description: {len(job_description)} characters")
        
        # Time the job matching
        print("\n🔍 Finding matching candidates...")
        matching_start = time.time()
        
        matches = query_engine.find_matching_resumes(job_description, top_k=5)
        
        matching_time = time.time() - matching_start
        performance_stats['job_matching'] = matching_time
        
        if not matches:
            print("❌ No matches found")
            return
        
        print(f"⏱️  Job matching completed in: {format_time(matching_time)}")
        
        # STEP 5: Results
        print_section("STEP 5: RESULTS")
        print("🏆 TOP MATCHING CANDIDATES:")
        print("-" * 50)
        
        for i, doc in enumerate(matches, 1):
            filename = doc.metadata['source']
            print(f"{i}. 📄 {filename}")
            print(f"   Preview: {doc.page_content[:150]}...")
            print()
        
        # STEP 6: Interactive Q&A with Individual Timing
        print_section("STEP 6: INTERACTIVE Q&A")
        print("🤖 Ask questions about candidates!")
        print("🚪 Type 'exit' to quit")
        print("💡 Each query will show individual timing")
        print("-" * 50)
        
        query_count = 0
        total_query_time = 0
        
        while True:
            question = input(f"\n❓ Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'bye']:
                break
            
            if not question:
                continue
            
            # Time individual query
            query_start = time.time()
            answer = query_engine.query(question)
            query_time = time.time() - query_start
            
            query_count += 1
            total_query_time += query_time
            
            print(f"\n🤖 Answer: {answer}")
            print(f"⏱️  Query processed in: {format_time(query_time)}")
        
        performance_stats['total_queries'] = query_count
        performance_stats['total_query_time'] = total_query_time
        performance_stats['average_query_time'] = total_query_time / query_count if query_count > 0 else 0
        
        # Final Performance Summary
        total_time = time.time() - total_start_time
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"🕐 Total Session Time: {format_time(total_time)}")
        print(f"📄 Resume Processing: {format_time(performance_stats['resume_processing'])}")
        print(f"🗃️  Vector Store Creation: {format_time(performance_stats['vector_store_creation'])}")
        print(f"🤖 AI Model Setup: {format_time(performance_stats['ai_model_setup'])}")
        print(f"🔍 Job Matching: {format_time(performance_stats['job_matching'])}")
        
        if query_count > 0:
            print(f"💬 Total Queries: {query_count}")
            print(f"⏱️  Total Query Time: {format_time(total_query_time)}")
            print(f"📈 Average Query Time: {format_time(performance_stats['average_query_time'])}")
            print(f"🚀 Queries per Second: {query_count/total_query_time:.2f}")
        
        # Efficiency Analysis
        print("\n📈 EFFICIENCY ANALYSIS:")
        print("-" * 30)
        setup_time = performance_stats['resume_processing'] + performance_stats['vector_store_creation'] + performance_stats['ai_model_setup']
        print(f"⚡ Setup Time: {format_time(setup_time)} ({setup_time/total_time*100:.1f}% of total)")
        print(f"🔍 Search Efficiency: {format_time(performance_stats['job_matching'])} for {len(matches)} results")
        
        if query_count > 0:
            print(f"💭 Q&A Efficiency: {format_time(performance_stats['average_query_time'])} per query")
        
        print("\n👋 Thanks for using the ATS!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
