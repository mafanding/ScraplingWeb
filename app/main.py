from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Optional
import anyio
import anyio.to_thread

from app.scraper import extract_links

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


class ScrapeRequest(BaseModel):
    url: str
    proxy: Optional[str] = None


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")


@app.post("/scrape")
async def scrape(req: ScrapeRequest):
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        return {"status": "error", "message": "Invalid URL scheme. Only http:// and https:// are supported."}

    proxy = req.proxy.strip() if req.proxy and req.proxy.strip() else None

    try:
        links, fetcher_used = await anyio.to_thread.run_sync(
            lambda: extract_links(url, proxy)
        )
        return {"status": "ok", "count": len(links), "links": links, "fetcher": fetcher_used}
    except Exception as e:
        return {"status": "error", "message": str(e)}
