"""
timer_utils.py — SmartyMS Timing Helper
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Har video/PDF ke liye:
  - Individual time (kitna laga ek file me)
  - Total batch time (sab files milake)
  - All Done message me grand total

Format: HH:MM:SS (agar >= 1 hour)
         MM:SS    (agar < 1 hour)
         SS sec   (agar < 1 min)
"""

import time


def fmt_time(seconds: float) -> str:
    """
    Seconds ko human-readable format me convert karo.
    Examples:
      3723  →  "01:02:03"
       125  →  "02:05"
        45  →  "45 sec"
    """
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    elif m > 0:
        return f"{m:02d}:{s:02d}"
    else:
        return f"{s} sec"


def fmt_time_full(seconds: float) -> str:
    """
    Hamesha HH:MM:SS format me return karo (All Done summary ke liye).
    Example: 3723 → "01:02:03"
    """
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class BatchTimer:
    """
    Ek puri batch (TXT file) ka time track karta hai.
    
    Usage:
        bt = BatchTimer(total_links=50)
        
        # Har file ke pehle:
        bt.start_item()
        
        # Har file ke baad:
        elapsed, eta = bt.finish_item()
        # elapsed = is file me kitna laga (formatted)
        # eta     = baaki files me kitna lagega (formatted)
    """

    def __init__(self, total_links: int):
        self.total        = total_links
        self.done         = 0
        self.batch_start  = time.time()
        self._item_start  = None

    def start_item(self):
        """Ek file ka timer shuru karo."""
        self._item_start = time.time()

    def finish_item(self):
        """
        File complete hone par call karo.
        Returns: (item_elapsed_str, eta_str, avg_per_item_str)
        """
        now = time.time()
        item_elapsed = now - (self._item_start or now)
        self.done += 1

        total_elapsed = now - self.batch_start
        remaining     = self.total - self.done

        if self.done > 0 and remaining > 0:
            avg = total_elapsed / self.done
            eta = avg * remaining
        else:
            eta = 0.0

        return fmt_time(item_elapsed), fmt_time(eta), fmt_time(total_elapsed)

    def total_elapsed(self) -> str:
        """Puri batch ka total time (All Done ke liye)."""
        return fmt_time_full(time.time() - self.batch_start)

    def total_elapsed_sec(self) -> float:
        return time.time() - self.batch_start
