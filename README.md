# ScraplingWeb

A zero-storage web link scraper with a clean web UI. Input a URL, extract all links, export as CSV.

Built with [Scrapling](https://github.com/D4Vinci/Scrapling), FastAPI, and vanilla JS. Runs as a single Docker container.

## Features

- Extract all `<a>` links from any webpage
- Displays link title and absolute URL in a table
- Optional proxy support
- One-click CSV export
- No database, no storage — stateless by design

## Quick Start

### Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8082
```

Open [http://localhost:8082](http://localhost:8082).

### Docker

```bash
docker compose up --build
```

Or with plain Docker:

```bash
docker build -t scraplingweb .
docker run -p 8082:8082 scraplingweb
```

## API

### `POST /scrape`

**Request:**
```json
{ "url": "https://example.com", "proxy": "http://user:pass@host:port" }
```

`proxy` is optional.

**Success response:**
```json
{ "status": "ok", "count": 42, "links": [{"title": "...", "url": "..."}] }
```

**Error response:**
```json
{ "status": "error", "message": "..." }
```

## Project Structure

```
ScraplingWeb/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── scraper.py       # Scrapling link extraction
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
