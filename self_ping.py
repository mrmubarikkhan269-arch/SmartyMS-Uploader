"""
self_ping.py — SmartyMS Bot Self-Pinger
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ye file bot ko khud hi apne aap ping karti rehti hai
taaki Render pe bina kisi bahari monitor (UptimeRobot wagera) ke
bot 24/7 alive rahe.

Kaise kaam karta hai:
  - RENDER_EXTERNAL_URL ya SERVICE_URL env var se apna URL leta hai
  - Har 4 minute me /health route ko ping karta hai
  - Agar URL nahi mila toh local server ko ping karta hai
  - main.py ke main() me asyncio.create_task() se chalta hai
"""

import asyncio
import os
import logging
from aiohttp import ClientSession, ClientTimeout, TCPConnector

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────

PING_INTERVAL = 4 * 60        # 4 minutes (Render 5 min me soti hai, hum pehle ping karenge)
PING_TIMEOUT  = ClientTimeout(total=30)

def get_service_url() -> str:
    """
    Service ka public URL dhundo.
    Render automatically RENDER_EXTERNAL_URL set karta hai.
    """
    url = (
        os.environ.get("RENDER_EXTERNAL_URL")
        or os.environ.get("SERVICE_URL")
        or os.environ.get("APP_URL")
    )
    if url:
        # Trailing slash hata do
        return url.rstrip("/")

    # Fallback: local health server
    PORT = int(os.environ.get("PORT", 8080))
    return f"http://0.0.0.0:{PORT}"


# ── Main ping loop ─────────────────────────────────────────────────────────────

async def self_ping_loop():
    """
    Har PING_INTERVAL seconds me /health ko ping karo.
    Isse main.py me asyncio.create_task(self_ping_loop()) se chalao.
    """
    await asyncio.sleep(15)  # Bot start hone ka thoda wait karo

    base_url = get_service_url()
    ping_url  = f"{base_url}/health"

    print(f"🔄 Self-pinger active → pinging {ping_url} every {PING_INTERVAL//60} min")
    logger.info(f"Self-pinger started: {ping_url}")

    connector = TCPConnector(ssl=False)   # HTTP aur HTTPS dono support

    async with ClientSession(connector=connector, timeout=PING_TIMEOUT) as session:
        while True:
            try:
                async with session.get(ping_url) as resp:
                    if resp.status == 200:
                        print(f"✅ Self-ping OK [{resp.status}] → {ping_url}")
                        logger.info(f"Self-ping OK: {resp.status}")
                    else:
                        print(f"⚠️ Self-ping got status {resp.status}")
                        logger.warning(f"Self-ping unexpected status: {resp.status}")

            except Exception as e:
                # Network error pe crash mat karo, sirf log karo
                print(f"⚠️ Self-ping failed (will retry): {e}")
                logger.warning(f"Self-ping error: {e}")

            await asyncio.sleep(PING_INTERVAL)
