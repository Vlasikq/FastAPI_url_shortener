from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from src.routers import links, users, link_previews

def create_app() -> FastAPI:
    app = FastAPI(title="My URL Shortener")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(links.router, prefix="/links", tags=["links"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(link_previews.router, prefix="/previews", tags=["link_previews"])
    return app

app = create_app()

