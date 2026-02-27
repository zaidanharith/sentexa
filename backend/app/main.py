from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)

@app.get("/")
def home():
     return {"message": "Welcome to Sentexa Backend"}

@app.get("/health")
def health():
     return {"status": "healthy"}

@app.exception_handler(404)
async def not_found(request: Request, exc):
     return JSONResponse(status_code=404, content={"error": "Not found"})

@app.exception_handler(500)
async def internal_error(request: Request, exc):
     return JSONResponse(status_code=500, content={"error": "Internal server error"})

if __name__ == "__main__":
     import uvicorn
     uvicorn.run(
          "main:app",
          host=os.getenv("HOST", "0.0.0.0"),
          port=int(os.getenv("PORT", 5000)),
          reload=os.getenv("FLASK_ENV", "development") == "development"
     )