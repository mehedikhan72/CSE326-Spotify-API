from fastapi import FastAPI

from app.controllers import collaboration, playback, playlist, share, tracks

app = FastAPI(
    title="Spotify Playlist Management API",
    description=(
        "API documentation for Spotify-like playlist management features.\n\n"
        "## Features\n"
        "- **Playlists** — Create, view, change details, and unfollow playlists\n"
        "- **Tracks** — Get, add, reorder, and remove playlist items\n"
        "- **Search** — Search the catalog and get recommendations\n"
        "- **Player** — Play, pause, seek, skip, and stop playback\n"
        "- **Collaboration** — Invite collaborators via link and manage access\n"
        "- **Share** — Generate shareable playlist links\n\n"
        "## Conventions\n"
        "- All IDs are Spotify IDs (strings), tracks are referenced by Spotify URIs.\n"
        "- Pagination uses `limit` and `offset` with `next`/`previous` cursor URLs.\n"
        "- Errors follow `{\"error\": {\"status\": int, \"message\": str}}` format.\n"
        "- Mutation endpoints on playlists return a `snapshot_id` for optimistic concurrency.\n"
        "- All endpoints require OAuth 2.0 authentication with appropriate scopes."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Playlists", "description": "Playlist CRUD and metadata management"},
        {"name": "Tracks", "description": "Playlist items — get, add, reorder, remove"},
        {"name": "Search", "description": "Search the catalog and get track recommendations"},
        {"name": "Player", "description": "Playback controls — play, pause, seek, skip, stop"},
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
