import uvicorn
from app import make_app

if __name__ == "__main__":
    app = make_app()

    uvicorn.run(
        app="app:make_app",
        port=8000,
        reload=True,
    )
