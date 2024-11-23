from fastapi import APIRouter, Request, Response
router = APIRouter()

@router.get("/")
async def index(request: Request, response: Response):
  return {"Hello": "World"}
