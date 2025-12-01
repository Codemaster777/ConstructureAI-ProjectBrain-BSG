
import json
import os
from langchain_groq import ChatGroq 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

DbPath = "./chroma_db"

def GetRagResponse(UserQuery):
    try:
        # 1. SETUP DATABASE
        EmbedModel = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        VectorDb = Chroma(persist_directory=DbPath, embedding_function=EmbedModel)
        
        # 2. RETRIEVE
        Retriever = VectorDb.as_retriever(search_kwargs={"k": 5})
        Docs = Retriever.invoke(UserQuery)
        ContextText = "\n\n".join([d.page_content for d in Docs])
        
        # 3. LLM
        Llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # 4. CHAIN
        SystemPrompt = "Answer based ONLY on context. If unsure, say unknown."
        PromptTemplate = ChatPromptTemplate.from_messages([
            ("system", SystemPrompt),
            ("human", "Context:\n{context}\n\nQuestion:\n{question}")
        ])
        Chain = PromptTemplate | Llm
        Response = Chain.invoke({"context": ContextText, "question": UserQuery})
        
        # 5. FORMAT SOURCES
        FormattedSources = []
        Seen = set()
        for d in Docs:
            # Safely get page number, default to '?' if missing
            Page = d.metadata.get("page", "?")
            Filename = d.metadata.get("filename", "Unknown")
            Key = f"{Filename}-{Page}"
            
            if Key not in Seen:
                FormattedSources.append({
                    "source": Filename,
                    "page": str(Page)
                })
                Seen.add(Key)

        return {"answer": Response.content, "sources": FormattedSources}

    except Exception as e:
        print(f"CHAT ERROR: {e}")
        return {"answer": f"System Error: {str(e)}", "sources": []}

def ExtractStructure(Requirement):
    try:
        # 1. SETUP
        EmbedModel = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        VectorDb = Chroma(persist_directory=DbPath, embedding_function=EmbedModel)
        # INCREASE K to find the table spread across pages
        Retriever = VectorDb.as_retriever(search_kwargs={"k": 15}) 
        Docs = Retriever.invoke(Requirement)
        ContextText = "\n\n".join([d.page_content for d in Docs])
        
        # 2. LLM
        Llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # 3. PROMPT 
        Prompt = f"""
        Extract the "{Requirement}" from the text.
        
        Look for a table with columns like: Door #, Wall Type, Frame Type, Door Type, Height, Width, Notes.
        
        Return ONLY valid JSON.
        Start the response with [ and end with ].
        Do NOT write "Here is the JSON".
        
        Use this Schema: 
        [
            {{
                "mark": "Door Number (e.g. 1, 2, D-101)",
                "frame_type": "Material (e.g. Hollow Metal, Aluminum)",
                "door_type": "Type (e.g. Single, Double Egress)",
                "size": "Height/Width info",
                "notes": "Any notes (e.g. AE601 TYP)"
            }}
        ]

        TEXT:
        {ContextText}
        """
        
        Response = Llm.invoke(Prompt)
        RawContent = Response.content
        
        # 4. ROBUST JSON PARSING
        try:
            Start = RawContent.find('[')
            End = RawContent.rfind(']') + 1
            if Start != -1 and End != 0:
                JsonStr = RawContent[Start:End]
                Data = json.loads(JsonStr)
            else:
                Data = json.loads(RawContent)
        except:
            print(f"JSON PARSE FAIL: {RawContent}")
            # If JSON fails, return empty list so UI doesn't crash
            Data = []
        
        # 5. FORMAT SOURCES
        FormattedSources = []
        Seen = set()
        for d in Docs:
            Page = d.metadata.get("page", "?")
            Filename = d.metadata.get("filename", "Unknown")
            Key = f"{Filename}-{Page}"
            if Key not in Seen:
                FormattedSources.append({
                    "source": Filename,
                    "page": str(Page)
                })
                Seen.add(Key)
        
        return {"data": Data, "sources": FormattedSources}

    except Exception as e:
        print(f"EXTRACTION ERROR: {e}")
        return {"data": [], "sources": []}