import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

DbPath = "./chroma_db"
DocsDir = "./Docs" 

def IngestDocuments():
    # 1. FORCE DELETE DB
    if os.path.exists(DbPath):
        try:
            shutil.rmtree(DbPath)
            print("CLEARED OLD DATABASE.")
        except:
            print("COULD NOT DELETE OLD DB. PLEASE DELETE 'chroma_db' FOLDER MANUALLY.")
            return

    # 2. CHECK DOCS
    if not os.path.exists(DocsDir):
        os.makedirs(DocsDir)
        print(f"ERROR: '{DocsDir}' NOT FOUND.")
        return

    AllChunks = []
    Files = [f for f in os.listdir(DocsDir) if f.endswith(".pdf")]
    
    if not Files:
        print("NO PDFS FOUND.")
        return

    # 3. PROCESS FILES
    for FileName in Files:
        FilePath = os.path.join(DocsDir, FileName)
        print(f"READING: {FileName}...")

        try:
            Loader = PyPDFLoader(FilePath)
            RawDocs = Loader.load()

            Splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                add_start_index=True
            )
            Chunks = Splitter.split_documents(RawDocs)

            # 4. INJECT PAGE NUMBERS
            for Chunk in Chunks:
                OldMeta = Chunk.metadata
                # PyPDF starts at 0, so we add 1
                PageNum = OldMeta.get("page", 0) + 1
                
                Chunk.metadata = {
                    "filename": FileName,
                    "source": FileName,
                    "page": str(PageNum) # Save as string to be safe
                }
            
            # Print first chunk to prove page number exists
            if Chunks:
                print(f"   -> Found {len(Chunks)} chunks. Sample Meta: {Chunks[0].metadata}")

            AllChunks.extend(Chunks)
            
        except Exception as e:
            print(f"   -> ERROR: {e}")

    # 5. SAVE TO DB
    if AllChunks:
        print(f"SAVING {len(AllChunks)} CHUNKS TO DB... (This may take a moment)")
        EmbedModel = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        VectorDb = Chroma.from_documents(
            documents=AllChunks,
            embedding=EmbedModel,
            persist_directory=DbPath
        )
        print("SUCCESS! INGESTION COMPLETE.")
    else:
        print("NO CHUNKS PROCESSED.")

if __name__ == "__main__":
    IngestDocuments()