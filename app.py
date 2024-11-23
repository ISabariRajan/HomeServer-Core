import uvicorn
from fastapi import FastAPI, APIRouter
from router import image_process, data_process

app = FastAPI()

@app.get("/")
async def index():
  print("Getting in")
  return {"Hello": " World"}

app.include_router(image_process.router, prefix="/image_process")
app.include_router(data_process.router, prefix="/data_process")

if __name__ == "__main__":
  uvicorn.run("app:app", host="localhost", port=8000, reload=True)