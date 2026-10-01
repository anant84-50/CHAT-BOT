import os
import re
from sqlalchemy.orm import Session
from .search_service import perform_search
from .rag_service import search_similar_chunks
from ..config import settings

def _is_search_required(query: str, llm=None) -> bool:
    if llm:
        try:
            prompt = f"Does the following user query require searching the web for up-to-date or external information? Reply with 'yes' or 'no' only.\nQuery: {query}"
            response = llm.invoke(prompt)
            return "yes" in response.content.lower()
        except Exception:
            pass
            
    # Heuristic detection for common queries that benefit from live search
    q = query.lower()
    search_keywords = [
        "weather", "today", "current", "latest", "news", "price", "stock",
        "who is", "what is", "where is", "when did", "search", "who won",
        "scores", "updates", "release date", "release", "2024", "2025", "2026"
    ]
    return any(k in q for k in search_keywords)

async def generate_response(message: str, history: list, db: Session, conversation_id: int):
    api_key = settings.LLM_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    sources = []
    context = ""
    
    # 1. RAG Check (Document context)
    rag_chunks = search_similar_chunks(message, conversation_id, db)
    if rag_chunks:
        context += "Relevant Document Content:\n" + "\n".join(rag_chunks) + "\n\n"
        
    llm = None
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Use gemini-2.5-flash or gemini-1.5-flash for speed and reliability
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
        except Exception:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
            except Exception:
                llm = None

    # 2. Web Search Check
    if _is_search_required(message, llm):
        search_results = perform_search(message)
        if search_results:
            sources.extend([{"title": r.get('title') or "Web source", "url": r.get('href') or ""} for r in search_results])
            context += "Web Search Results:\n" + "\n".join([f"- {r.get('title')}: {r.get('body')}" for r in search_results]) + "\n\n"
    
    # 3. If LLM is available, generate response
    if llm:
        sys_prompt = (
            "You are a helpful Multimodal AI Chatbot. Answer the user's questions clearly, accurately, and politely. "
            "If context from web searches or documents is provided, use it to inform your answer. "
            "Be conversational, structured, and empathetic when appropriate."
        )
        messages = [("system", sys_prompt)]
        if context:
            messages.append(("system", f"Context available:\n{context}"))
        for msg in history:
            messages.append((msg["role"], msg["content"]))
            
        try:
            response = llm.invoke(messages)
            return response.content, sources
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            # Fall through to fallback response
    
    # 4. Fallback when LLM API key is not configured or LLM failed
    if rag_chunks:
        doc_snippet = "\n\n".join(rag_chunks[:2])
        reply = (
            f"Here is what I found in your uploaded document matching your query:\n\n"
            f"{doc_snippet}\n\n"
            f"*(Tip: To enable advanced AI reasoning, summaries, and synthesis, add your `LLM_API_KEY` in the `.env` file.)*"
        )
        return reply, sources

    if sources:
        snippets = []
        for s in sources[:3]:
            title = s.get('title')
            url = s.get('url')
            snippets.append(f"• **{title}**\n  [Link]({url})")
        reply = (
            f"I found the following web search results for **'{message}'**:\n\n" +
            "\n".join(snippets) +
            f"\n\n*(Add your `LLM_API_KEY` in the `.env` file to enable full AI summaries of search results!)*"
        )
        return reply, sources

    if not api_key:
        return (
            "Hello! I am your Multimodal AI Chatbot.\n\n"
            "Here is what I can do:\n"
            "1. **Live Web Search**: Ask questions like *'latest tech news'* or *'weather today'* to search the web in real-time.\n"
            "2. **Document Q&A (RAG)**: Click the paperclip icon to upload a PDF, DOCX, or TXT file and ask questions about it.\n"
            "3. **AI Generation**: Add your Gemini API key in the `.env` file (`LLM_API_KEY=...`) to enable full generative responses!"
        ), []

    return "I'm sorry, I was unable to generate a response at this time. Please check your network and API key settings.", sources

