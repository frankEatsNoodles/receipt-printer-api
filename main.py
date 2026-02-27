import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api:app",  # Changed from "main:app" to "api:app"
        host="127.0.0.1",
        port=8000,
        reload=True
    )