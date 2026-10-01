# Multimodal AI Chatbot MVP

## Project Objective
A beginner-friendly Multimodal AI Chatbot that can understand multiple types of user inputs (text, image, docs, audio) and generate multiple types of outputs. This MVP focuses on text chat, document understanding (RAG), web search, and document creation/editing.

## Key Features
- **Multimodal Interaction**: Chat with text, upload images, PDFs, and DOCX files.
- **RAG (Retrieval-Augmented Generation)**: Answers questions based on uploaded documents.
- **Web Search**: Automatically searches the web for current information if required.
- **Document Creation/Editing**: Request changes to a document and download the new version.
- **Emotional Assistance**: Empathetic conversation capabilities built-in through prompt design.
- **Modern UI**: A beautiful, responsive chat interface built with React.

## Technology Stack
- **Frontend**: React (Vite), TypeScript, Vanilla CSS
- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (with pgvector for embeddings if configured)
- **AI**: Gemini 1.5 Pro via `langchain-google-genai` and `google-genai`

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (running locally or remote)

## Environment Variables
Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
LLM_API_KEY=your_gemini_api_key_here
SEARCH_API_KEY=your_search_api_key_here
```

## Setup Instructions

### Backend
1. Navigate to `backend/`: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`
The API will be available at http://localhost:8000

### Frontend
1. Navigate to `frontend/`: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`
The UI will be available at http://localhost:5173

## Workflows
- **RAG Workflow**: Upload a PDF. The backend extracts text, chunks it, generates embeddings, and saves to PostgreSQL. When you ask a question, it retrieves similar chunks and uses them as context.
- **Web Search Workflow**: If you ask "What's the weather today?", the LLM detects it needs external info, performs a DuckDuckGo search, and answers using the results, citing sources.

## Limitations
- This is an MVP and does not include user authentication or complex agentic frameworks.
- Audio transcription and TTS endpoints exist as placeholders in the codebase for future extension.
