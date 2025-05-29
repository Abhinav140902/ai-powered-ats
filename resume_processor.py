import os
import time
import pypdf
import docx2txt
from typing import List, Tuple

class ResumeProcessor:
    def __init__(self, resume_dir: str = "data/resumes"):
        self.resume_dir = resume_dir
        os.makedirs(resume_dir, exist_ok=True)
        
    def load_resumes(self) -> List[Tuple[str, str]]:
        load_start = time.time()
        resume_texts = []
        
        if not os.path.exists(self.resume_dir):
            print(f"❌ Directory {self.resume_dir} not found")
            return resume_texts
            
        files = os.listdir(self.resume_dir)
        if not files:
            print(f"📁 No files found in {self.resume_dir}")
            return resume_texts
        
        total_chars = 0
        
        for filename in files:
            file_start = time.time()
            file_path = os.path.join(self.resume_dir, filename)
            
            print(f"📄 Processing: {filename}")
            
            if filename.lower().endswith('.pdf'):
                text = self._extract_from_pdf(file_path)
            elif filename.lower().endswith('.docx'):
                text = self._extract_from_docx(file_path)
            else:
                print(f"⚠️  Skipping unsupported file: {filename}")
                continue
            
            file_time = time.time() - file_start
            
            if text and text.strip():
                resume_texts.append((filename, text))
                total_chars += len(text)
                print(f"✅ Successfully processed: {filename} ({len(text)} chars) in {file_time:.2f}s")
            else:
                print(f"❌ Failed to extract text from: {filename} in {file_time:.2f}s")
        
        total_time = time.time() - load_start
        print(f"📊 Processing summary:")
        print(f"   ⏱️  Total time: {total_time:.2f}s")
        print(f"   📄 Files processed: {len(resume_texts)}")
        print(f"   📝 Total characters: {total_chars:,}")
        if total_time > 0:
            print(f"   🚀 Processing speed: {len(resume_texts)/total_time:.1f} files/second")
            print(f"   📊 Character rate: {total_chars/total_time:,.0f} chars/second")
        
        return resume_texts
    
    def _extract_from_pdf(self, file_path: str) -> str:
        extract_start = time.time()
        try:
            text = ""
            reader = pypdf.PdfReader(file_path)
            
            for page_num, page in enumerate(reader.pages):
                page_start = time.time()
                page_text = page.extract_text()
                page_time = time.time() - page_start
                
                if page_text:
                    text += page_text + "\n"
                    print(f"     📄 Page {page_num+1}: {len(page_text)} chars in {page_time*1000:.1f}ms")
            
            extract_time = time.time() - extract_start
            print(f"     ⏱️  PDF extraction: {extract_time:.3f}s total")
            return text.strip()
            
        except Exception as e:
            extract_time = time.time() - extract_start
            print(f"❌ PDF extraction error for {file_path} after {extract_time:.2f}s: {str(e)}")
            return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        extract_start = time.time()
        try:
            text = docx2txt.process(file_path)
            extract_time = time.time() - extract_start
            print(f"     ⏱️  DOCX extraction: {extract_time:.3f}s")
            return text.strip() if text else ""
            
        except Exception as e:
            extract_time = time.time() - extract_start
            print(f"❌ DOCX extraction error for {file_path} after {extract_time:.2f}s: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        
        clean_start = time.time()
        
        import re
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        clean_time = time.time() - clean_start
        if clean_time > 0.001:  # Only show if > 1ms
            print(f"     🧹 Text cleaning: {clean_time*1000:.1f}ms")
        
        return cleaned
