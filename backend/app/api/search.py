from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def search_placeholder():
    return {"message": "Search API - Not strictly necessary as search is done internally by LLM service"}
