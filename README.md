# Constructure Technical Assignment - Project Brain

This repository contains the submission for the Applied LLM Engineer technical challenge (36-Hour). The application functions as a construction intelligence agent, capable of ingesting technical documentation (PDF specifications and drawings) to facilitate both natural language retrieval (RAG) and structured data extraction.

## Deployment Status

The application has been deployed to the following environments:

*   **Frontend (Interface):** [https://projectbrain.vercel.app](https://projectbrain.vercel.app/)
*   **Backend (API):** [https://bhanushray-project-brain-backend.hf.space](https://bhanushray-project-brain-backend.hf.space)

> **Note:** The backend is hosted on a free-tier container which may spin down during inactivity. Upon initial load, the **"Reset Ingestion"** button in the application header should be clicked to re-initialize the vector index.

---

## System Architecture

The solution is architected as a decoupled system using FastAPI for the inference layer and Next.js for the user interface.

### 1. Retrieval & Generation (RAG)
Document ingestion is handled via `PyPDFLoader`, with text being segmented using recursive character splitting to maintain semantic context across chunks.
*   **Vectorization:** Local embeddings (`all-MiniLM-L6-v2`) are generated via HuggingFace to ensure the backend remains self-contained and cost-efficient.
*   **Storage:** ChromaDB is utilized for vector persistence.
*   **Citations:** Page numbers and filenames are extracted during ingestion and preserved in metadata, ensuring every AI response is cited with exact location references (e.g., `Drawings.pdf (p. 5)`).

### 2. Structured Extraction Engine
A routing layer was implemented to distinguish between general inquiries and extraction commands.
*   **Intent Detection:** Queries containing specific keywords (e.g., "schedule", "list") are routed to a strict extraction pipeline.
*   **Schema Enforcement:** Prompts are engineered to enforce specific JSON schemas. A custom parsing logic was developed to strip conversational text from LLM outputs, ensuring the frontend receives clean JSON for data grid rendering.

### 3. Model Selection
**Llama-3-70b (via Groq)** was selected as the inference engine. This choice was driven by the need for near-instant latency to maintain a fluid chat experience, while providing reasoning capabilities comparable to proprietary models.

---

## Technical Stack

*   **Frontend:** Next.js 14 (App Router), Tailwind CSS.
*   **Backend:** FastAPI, Python 3.11.
*   **Orchestration:** LangChain.
*   **Database:** ChromaDB (Local).
*   **Inference:** Groq API (Llama-3-70b).

---

## Local Setup Instructions

### Backend Configuration
The backend requires Python 3.10+ and a valid Groq API key.

1.  Navigate to the backend directory:
    ```bash
    cd Backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure environment variables in a `.env` file:
    ```properties
    GROQ_API_KEY=gsk_your_key_here
    ```
4.  Initialize the vector database:
    ```bash
    python ingestion.py
    ```
5.  Start the API server:
    ```bash
    python Server.py
    ```

### Frontend Configuration
1.  Navigate to the frontend directory:
    ```bash
    cd Frontend
    ```
2.  Install dependencies and start the development server:
    ```bash
    npm install
    npm run dev
    ```
3.  Access the application at `http://localhost:3000` using the test credentials: `testingcheckuser1234@gmail.com`.

---

## Automated Evaluation

An evaluation script (`TestEval.py`) is included to verify core functionality against the requirements. It tests both the retrieval quality (checking for citations) and the extraction logic (checking for valid JSON arrays).

**Latest Evaluation Results:**

```text
========================================
   PROJECT BRAIN - AUTOMATED EVALUATION
========================================
Target API: http://localhost:8000

TEST #1: [CHAT] 'What is the fire rating for corridor partitions?'
   -> PASS (12.52s) - Answer length > 10 chars.
----------------------------------------
TEST #2: [CHAT] 'What is the flooring material in the lobby?'
   -> PASS (7.78s) - Found 3 sources.
----------------------------------------
TEST #3: [EXTRACT] 'Generate a door schedule'
   -> PASS (9.2s) - Extracted 9 rows.
----------------------------------------
TEST #4: [CHAT] 'Who is the architect?'
   -> PASS (8.5s) - Answer length > 10 chars.
----------------------------------------

SUMMARY: 4 PASSED | 0 FAILED
========================================
