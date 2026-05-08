"""
health.py — SmartyMS Bot Health Check Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ye file aiohttp ka use karke ek lightweight web server chalati hai
jo Render ko batati hai ke bot zinda hai (HTTP health check).

Routes:
  GET /         → 200 OK (basic ping)
  GET /health   → 200 OK JSON status
  HEAD /        → 200 OK (UptimeRobot style HEAD ping)
  HEAD /health  → 200 OK

Kaise kaam karta hai:
  - main.py ke main() me start_health_server() call hoti hai
  - Render ka PORT env var use hota hai (default 8080)
  - Saath hi self_ping.py apne aap is server ko ping karta rehta hai
"""

import asyncio
import os
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

# ── Routes ────────────────────────────────────────────────────────────────────

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok",
        "bot": "SmartyMS Uploader Bot",
        "message": "Bot is alive and running! 🤖"
    })

@routes.get("/health", allow_head=True)
async def health_handler(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "healthy",
        "bot": "SmartyMS Uploader Bot",
        "uptime": "running",
        "message": "✅ Bot is active 24/7"
    })

# ── Server startup ─────────────────────────────────────────────────────────────

async def start_health_server():
    """
    Health check web server start karo.
    Isse main.py ke main() me asyncio task ki tarah chalao.
    """
    PORT = int(os.environ.get("PORT", 8080))

    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"✅ Health server started on port {PORT}")
    print(f"✅ Health server started → http://0.0.0.0:{PORT}/health")

    # Server hamesha chalta rahe
    while True:
        await asyncio.sleep(3600)
