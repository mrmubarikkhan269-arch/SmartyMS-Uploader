"""
live_timer.py — SmartyMS Live Countdown Timer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Download ke dauran prog message ko live update karta hai.
Har 3 second mein elapsed time badh jaata hai aur message edit hota hai.

Format:
  45s → 42s → 39s  (jab < 2 min)
  2m 45s → 2m 42s  (jab >= 2 min)
  1h 5m 12s         (jab >= 1 hour)

Usage (main.py mein):
    stop_event = asyncio.Event()
    task = asyncio.create_task(
        live_download_timer(prog, base_text, stop_event)
    )
    res_file = await helper.download_video(...)
    stop_event.set()
    await task
"""

import asyncio
import time


def _fmt_live(seconds: int) -> str:
    """
    Seconds ko live-display format me convert karo.
    Examples:
      45   →  "45s"
      125  →  "2m 05s"
      3723 →  "1h 02m 03s"
    """
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    elif m > 0:
        return f"{m}m {s:02d}s"
    else:
        return f"{s}s"


async def live_download_timer(prog, base_text: str, stop_event: asyncio.Event):
    """
    Download ke dauran prog message ko har 3 sec mein edit karta hai.
    Elapsed time countdown style mein dikhata hai (upar jaata hai).

    Args:
        prog       : Pyrogram Message object (jo edit hoga)
        base_text  : Original Show message text
        stop_event : asyncio.Event — download complete hone par .set() karo
    """
    start = time.time()
    interval = 3  # har 3 second mein update

    while not stop_event.is_set():
        await asyncio.sleep(interval)
        if stop_event.is_set():
            break

        elapsed = int(time.time() - start)
        live_str = _fmt_live(elapsed)

        try:
            await prog.edit(
                base_text + f"\n\n⏱️ **Elapsed:** `{live_str}`"
            )
        except Exception:
            # FloodWait ya koi aur error → sirf skip karo, crash mat karo
            pass


async def live_upload_elapsed(reply, base_build_fn, stop_event: asyncio.Event):
    """
    Upload ke dauran bhi elapsed time dikhata hai.
    (utils.py ke progress_bar ke saath use hota hai)

    Args:
        reply        : Pyrogram Message object
        base_build_fn: callable jo current progress text return kare
        stop_event   : asyncio.Event
    """
    # utils.py ka progress_bar khud edit karta hai, ye sirf fallback hai
    # is function ko seedha call karne ki zaroorat nahi normally
    pass
