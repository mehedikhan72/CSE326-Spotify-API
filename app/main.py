from fastapi import FastAPI

from app.controllers import collaboration, playback, playlist, share, tracks

app = FastAPI(
    title="Spotify Playlist Management API",
    description=(
        "API documentation for Spotify-like playlist management features.\n\n"
        "## Features\n"
        "- **Playlists** — Create, view, update metadata, and delete playlists\n"
        "- **Tracks** — Search the catalog, add tracks to playlists, reorder, and remove\n"
        "- **Playback** — Play, pause, resume, skip, seek, and stop music\n"
        "- **Collaboration** — Invite collaborators via link and manage access\n"
        "- **Share** — Generate shareable playlist links\n\n"
        "## Notes\n"
        "- All endpoints assume an authenticated user context (auth to be implemented).\n"
        "- UUIDs are used for all entity identifiers.\n"
        "- Responses follow consistent error schemas across all endpoints."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Playlists", "description": "Playlist CRUD operations and metadata management"},
        {"name": "Tracks", "description": "Track management within playlists (add, reorder, remove)"},
        {"name": "Search", "description": "Search the track catalog and get suggestions"},
        {"name": "Playback", "description": "Music playback controls (play, pause, seek, next, stop)"},
        {"name": "Collaboration", "description": "Collaborative playlist invite and member management"},
        {"name": "Share", "description": "Playlist sharing via link"},
    ],
)

app.include_router(playlist.router)
app.include_router(tracks.router)
app.include_router(playback.router)
app.include_router(collaboration.router)
app.include_router(share.router)


@app.get("/health", tags=["Health"], summary="Health check")
async def health_check():
    """Check if the API is running."""
    return {"status": "ok"}
