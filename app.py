"""
WSGI entry point for deployment on Beget
"""
from backend.api.main import app

# This is the WSGI application object that Beget will look for
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)