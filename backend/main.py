import uvicorn



if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # Reference the app instance, not the factory
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
