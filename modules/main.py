import os
import re
import sys
import json
import time
import random
import asyncio
import requests
import subprocess
import urllib.parse
import yt_dlp
import cloudscraper
import m3u8
import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ── Simple in-memory user store (replace with DB if needed) ──────────────────
_user_ids: set = set()

class db:
    @staticmethod
    def register_user(user_id: int):
        _user_ids.add(user_id)

    @staticmethod
    def get_all_user_ids():
        return list(_user_ids)
# ─────────────────────────────────────────────────────────────────────────────

# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔎Developer", url="https://t.me/SmartBoy_ApnaMS")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="🛠️ Channel", url="https://t.me/Toxic_Official_1"),
            InlineKeyboardButton(text="👑 Owner", url="https://t.me/MR_Toxic_1"),
        ],
        [
            InlineKeyboardButton(text="🔎 Developers", url="https://t.me/SmartBoy_ApnaMS"),
        ],
    ]
)

my_name = "MS"

# ── Live-changeable API endpoints (owner can update via /changeapi) ──────────
# Both PWAPI1 and PWAPI2 always stay in sync — use /changeapi to update both
PWAPI1 = "https://anonymouspwplayerr-3cfbfedeb317.herokuapp.com/pw"
PWAPI2 = "https://anonymouspwplayerr-3cfbfedeb317.herokuapp.com/pw"
# ─────────────────────────────────────────────────────────────────────────────

# ── Random image list (add/remove URLs freely) ────────────────────────────────
image_list = [
    "https://graph.org/file/9427b9e9e643d29bcaf33-aa5c8b67c163a9c4a2.jpg",
    "https://graph.org/file/77656b3519aae1826dd7a-16b8aafc835d99d6f1.jpg",
    "https://graph.org/file/5e0485a8e5db299de606b-3156b543bd2a963740.jpg",
    "https://graph.org/file/17bb023117043bb942185-96bf90a807fef3e18d.jpg",
    "https://graph.org/file/065fa6a3871e2de715e3a-f774a3a3bad574c214.jpg",
    "https://graph.org/file/7da497bca809e08f89898-bf746d8ce14d321a4f.jpg",
    "https://graph.org/file/c2f371599c84453293f1a-f1fb1a7bdb872a6e1a.jpg",
]
# ─────────────────────────────────────────────────────────────────────────────

cookies_file_path = os.getenv("COOKIES_FILE_PATH", "/modules/youtube_cookies.txt")

# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("https://text-leech-bot-for-render.onrender.com/")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def main():
    WEBHOOK = os.getenv("WEBHOOK", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 8080))

    if WEBHOOK:
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    await bot.start()
    print("Bot is up and running")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await bot.stop()

        
class Data:
    START = (
        "🌟 Welcome Dear🤝 {0}! 🌟\n\n"
    )


# ── Credit name href parser ────────────────────────────────────────────────────
# Supports: "Text|https://url" → "[Text](https://url)" (Telegram markdown link)
# Normal text with no "|" passes through unchanged.
def parse_credit(raw: str) -> str:
    if "|" in raw:
        parts = raw.split("|", 1)
        text = parts[0].strip()
        url  = parts[1].strip()
        return f"[{text}]({url})"
    return raw
# ─────────────────────────────────────────────────────────────────────────────

# ── /start command — with animated progress + image reply ─────────────────────
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    db.register_user(msg.from_user.id)
    start_message = await msg.reply_text(
        Data.START.format(msg.from_user.mention)
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Initializing Uploader bot... 🤖\n\n"
        "Progress: [⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Loading features... ⏳\n\n"
        "Progress: [🟥🟥🟥⬜⬜⬜⬜⬜⬜] 25%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "This may take a moment, sit back and relax! 🥵\n\n"
        "Progress: [🟧🟧🟧🟧🟧⬜⬜⬜⬜] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking Bot Status... 🔍\n\n"
        "Progress: [🟨🟨🟨🟨🟨🟨🟨⬜⬜] 75%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.delete()

    # ── Send random image with caption as a REPLY to the user's /start ────────
    await client.send_photo(
        chat_id=msg.chat.id,
        photo=random.choice(image_list),
        caption=(
            Data.START.format(msg.from_user.mention) +
            "✅ Bot Ready! Command is Private Dear.🌚\n"
            "**Bot Made BY Developer Brother** 🔍\n\n"
            "Meet to my /Owner Now🤩.\n"
            "Progress: [🟩🟩🟩🟩🟩🟩🟩🟩🟩] 100%\n\n"
        ),
        reply_markup=keyboard,
        reply_to_message_id=msg.id      # ← makes it a reply to user's message
    )


# ── /stop command ──────────────────────────────────────────────────────────────
@bot.on_message(filters.command(["stop"]))
async def restart_handler(_, m: Message):
    await m.reply_text("🌺**STOPPED**🌺", True)
    os.execl(sys.executable, sys.executable, *sys.argv)


# ── /owner command ─────────────────────────────────────────────────────────────
@bot.on_message(filters.command("owner"))
async def owner_handler(client: Client, msg: Message):
    db.register_user(msg.from_user.id)

    owner_text = (
        "┌──────────────────────────┐\n"
        "**My Owner**:@SmartBoy_ApnaMS\n"
        "└──────────────────────────┘\n\n"
    )

    await msg.reply_text(owner_text)


# ── /broadcast command (owner only) ───────────────────────────────────────────
@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, msg: Message):
    if msg.from_user.id != OWNER:
        return await msg.reply_text("you are not my owner 😒.")

    if not msg.reply_to_message:
        return await msg.reply_text(
            "📢 **Broadcast Mode**\n\n"
            "please Boss reply with such a content for broadcasting."
        )

    content = msg.reply_to_message
    all_users = db.get_all_user_ids()

    if not all_users:
        return await msg.reply_text("❌ No users in database yet.")

    sent = 0
    failed = 0
    status_msg = await msg.reply_text(f"📤 Broadcasting to `{len(all_users)}` users...")

    for user_id in all_users:
        try:
            await content.copy(user_id)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # small delay to avoid flood

    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"📨 Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`\n"
        f"👥 Total: `{len(all_users)}`"
    )


# ── /Mahi command ──────────────────────────────────────────────────────────────
@bot.on_message(filters.command(["Sobi"]))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"**🔹Hi I am Poweful Lovely TXT Downloader📥 Bot.**\n🔹**Send me the TXT file and Just wait and Watch😚.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = f"@Lapata_786"
    token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzYxNTE3MzAuMTI2LCJkYXRhIjp7Il9pZCI6IjYzMDRjMmY3Yzc5NjBlMDAxODAwNDQ4NyIsInVzZXJuYW1lIjoiNzc2MTAxNzc3MCIsImZpcnN0TmFtZSI6IkplZXYgbmFyYXlhbiIsImxhc3ROYW1lIjoic2FoIiwib3JnYW5pemF0aW9uIjp7Il9pZCI6IjVlYjM5M2VlOTVmYWI3NDY4YTc5ZDE4OSIsIndlYnNpdGUiOiJwaHlzaWNzd2FsbGFoLmNvbSIsIm5hbWUiOiJQaHlzaWNzd2FsbGFoIn0sImVtYWlsIjoiV1dXLkpFRVZOQVJBWUFOU0FIQEdNQUlMLkNPTSIsInJvbGVzIjpbIjViMjdiZDk2NTg0MmY5NTBhNzc4YzZlZiJdLCJjb3VudHJ5R3JvdXAiOiJJTiIsInR5cGUiOiJVU0VSIn0sImlhdCI6MTczNTU0NjkzMH0.iImf90mFu_cI-xINBv4t0jVz-rWK1zeXOIwIFvkrS0M"
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Hii saitan .🌚🤣")
        os.remove(x)
        return
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download🤔 initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1
    await editable.edit("**Enter Your Batch Name or send '/up' for grabing from text filename.😉**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == '/up':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 144, 250, 360, 480, 720 or 1080😚**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    
    await editable.edit("**Enter Your Name or send '/Mahi' for use default.🌚\n Eg :@Lapata_786 **")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == '/Mahi':
        CR = credit
    else:
        CR = raw_text3
        
    await editable.edit("**Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋  or send '/Mahi' for use default🎀**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    if raw_text4 == '/Mahi':
        MR = token
    else:
        MR = raw_text4
        
    await editable.edit("Now send the **Thumb url**\n**Eg: Who's End With .jpg** ``\n\nor Send `no`")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    count = int(raw_text)    
    try:
        for i in range(arg-1, len(links)):


            # Skip lines with no valid URL (e.g. 'None' or missing '://')
            if len(links[i]) < 2 or not links[i][1].strip() or links[i][1].strip().lower() == 'none':
                count += 1
                continue

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'
                

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'classplusapp' in url or "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                url, contentId = url.split('&', 1)
                
                headers = {
                    'host': 'api.classplusapp.com',
                    'x-access-token': f'{cp_token}',    
                    'accept-language': 'EN',
                    'api-version': '18',
                    'app-version': '1.4.73.2',
                    'build-number': '35',
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'device-details': 'Xiaomi_Redmi 7_SDK-32',
                    'device-id': 'c28d3cb16bbdac01',
                    'region': 'IN',
                    'user-agent': 'Mobile-Android',
                    'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
                    'accept-encoding': 'gzip'
                }
                
                params = {
                    'contentId': contentId,
                    'offlineDownload': "false"
                }

                url = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json().get("url")

            
            #elif '/master.mpd' in url:
             #id =  url.split("/")[-2]
             #url = f"https://player.muftukmall.site/?id={id}"
            #elif '/master.mpd' in url:
             #id =  url.split("/")[-2]
             #url = f"{PWAPI1}?url={url}?token={raw_text4}"
            #url = f"https://madxapi-d0cbf6ac738c.herokuapp.com/{id}/master.m3u8?token={raw_text4}"
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
             url = f"{PWAPI2}?url={url}&token={raw_text4}"
                     
                                                         
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'
                      
            
            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
                url = url.split("bcov_auth")[0]+bcov
                
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'

            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                
                cc = f'**📹 VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {res}.mkv\n\n<pre><code>📚 Batch Name: {b_name}</code></pre>\n\n📥 Extracted By♠ : {CR}\n\n**∘₊❀━━━𓆩Mคɦɨ𓆪━━━❀₊∘**'
                cc1 = f'**💾 PDF_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} .pdf\n\n<pre><code>📚 Batch Name: {b_name}</code></pre>\n\n📥 Extracted By♠ : {CR}\n\n**∘₊❀━━━𓆩Mคɦɨ𓆪━━━❀₊∘**'
                    
                
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        await asyncio.sleep(4)
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)

                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)

                            await asyncio.sleep(4)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        else:
                            await m.reply_text(f"Failed to download PDF: {response.status_code} {response.reason}")

                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                          
                else:
                    Show = f"✰🖥️ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝗪𝗮𝗶𝘁..🤖🚀 »\n\n📝 Title:- `{name}\n\n📹 𝐐𝐮𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**🔗 𝐔𝐑𝐋 »** `{url}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲🧸: ✦ @Lapata_786 ❖"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘✰𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝗙𝗮𝗶𝗹𝗲𝗱⛔\n\n⌘ 𝐍𝐚𝐦𝐞🌟 » {name}\n⌘ 𝐋𝐢𝐧𝐤🖥️ » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("𝐀𝐋𝐋 𝐃𝐎𝐍𝐄 Reaction khud de doge ya kahna padega ✅🔸")


# ── /Ali command ───────────────────────────────────────────────────────────────
@bot.on_message(filters.command(["Boy"]))
async def ali_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"**🔹Hi I am Poweful Lovely TXT Downloader📥 Bot.**\n🔹**Send me the TXT file and Just wait and Watch🥵.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = f"@Lapata_786"
    token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzYxNTE3MzAuMTI2LCJkYXRhIjp7Il9pZCI6IjYzMDRjMmY3Yzc5NjBlMDAxODAwNDQ4NyIsInVzZXJuYW1lIjoiNzc2MTAxNzc3MCIsImZpcnN0TmFtZSI6IkplZXYgbmFyYXlhbiIsImxhc3ROYW1lIjoic2FoIiwib3JnYW5pemF0aW9uIjp7Il9pZCI6IjVlYjM5M2VlOTVmYWI3NDY4YTc5ZDE4OSIsIndlYnNpdGUiOiJwaHlzaWNzd2FsbGFoLmNvbSIsIm5hbWUiOiJQaHlzaWNzd2FsbGFoIn0sImVtYWlsIjoiV1dXLkpFRVZOQVJBWUFOU0FIQEdNQUlMLkNPTSIsInJvbGVzIjpbIjViMjdiZDk2NTg0MmY5NTBhNzc4YzZlZiJdLCJjb3VudHJ5R3JvdXAiOiJJTiIsInR5cGUiOiJVU0VSIn0sImlhdCI6MTczNTU0NjkzMH0.iImf90mFu_cI-xINBv4t0jVz-rWK1zeXOIwIFvkrS0M"
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Hii saitan.🌚😘")
        os.remove(x)
        return
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download🤔 initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1
    await editable.edit("**Enter Your Batch Name or send '/Mahi' for grabing from text filename.🌚**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == '/Mahi':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 144, 240, 360, 480, 720 or 1080😚**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    
    await editable.edit("**Enter Your Name or send '/Mahi' for use default.😗\n Eg : @Lapata_786**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == '/Mahi':
        CR = credit
    else:
        CR = raw_text3
        
    await editable.edit("Now send the **Thumb url**\n**Eg Who's End With .jpg:** ``\n\nor Send `no`")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    count = int(raw_text)    
    try:
        for i in range(arg-1, len(links)):


            # Skip lines with no valid URL (e.g. 'None' or missing '://')
            if len(links[i]) < 2 or not links[i][1].strip() or links[i][1].strip().lower() == 'none':
                count += 1
                continue

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'
                

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'classplusapp' in url or "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                url, contentId = url.split('&', 1)
                
                headers = {
                    'host': 'api.classplusapp.com',
                    'x-access-token': f'{cp_token}',    
                    'accept-language': 'EN',
                    'api-version': '18',
                    'app-version': '1.4.73.2',
                    'build-number': '35',
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'device-details': 'Xiaomi_Redmi 7_SDK-32',
                    'device-id': 'c28d3cb16bbdac01',
                    'region': 'IN',
                    'user-agent': 'Mobile-Android',
                    'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
                    'accept-encoding': 'gzip'
                }
                
                params = {
                    'contentId': contentId,
                    'offlineDownload': "false"
                }

                url = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json().get("url")

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                    
                elif 'Key-Pair-Id' in url:
                    url = None
                    
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)
                    
            elif '/master.mpd' in url:
             vid_id =  url.split("/")[-2]
             url =  f"https://pw-url-api-v1mf.onrender.com/process?v=https://sec1.pw.live/{vid_id}/master.mpd&quality={raw_text2}"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'
          

            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
                url = url.split("bcov_auth")[0]+bcov
                
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'

            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
        
                cc = f'**📹 VID_ID: {str(count).zfill(3)}.\n\nTitle: {name1} STUDENTS💛{res}.mkv\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By♠ : {CR}\n\n**∘₊✿━━━✿༄Mahi✿━━━✿₊∘**'
                cc1 = f'**💾 PDF_ID: {str(count).zfill(3)}.\n\nTitle: {name1} STUDENTS💛.pdf\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By♠ : {CR}\n\n**∘₊✿━━━✿༄Mahi✿━━━✿₊∘**'
                    
                
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        await asyncio.sleep(4)
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)

                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)

                            await asyncio.sleep(4)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        else:
                            await m.reply_text(f"Failed to download PDF: {response.status_code} {response.reason}")

                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                          
                else:
                    Show = f"✰🖥️𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝗪𝗮𝗶𝘁..🤖🚀»\n\n📝 Title:- `{name}\n\n🖥️ 𝐐𝐮𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**🔗 𝐔𝐑𝐋 »** `{url}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲🧸: ✦ @Lapata_786✰"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝗙𝗮𝗶𝗹𝗲𝗱⛔\n\n⌘ 𝐍𝐚𝐦𝐞🌟 » {name}\n⌘ 𝐋𝐢𝐧𝐤 » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("𝐀𝐋𝐋 𝐃𝐎𝐍𝐄 REACTIONS khud doge ya kahna padega .✅🔸")


# ── /changeapi command (owner only) ───────────────────────────────────────────
# Usage: /changeapi https://new-api.example.com/pw
# Updates both PWAPI1 and PWAPI2 at once (they always use the same API)
@bot.on_message(filters.command("changeapi") & filters.private)
async def changeapi_handler(client: Client, msg: Message):
    global PWAPI1, PWAPI2
    if msg.from_user.id != OWNER:
        return await msg.reply_text(
            "To change your Api in your Repository in this format\n\n"
            "/changeapi New Api Here\n\n"
            "But But But🫡\n"
            "Sorry you are not my owner😒."
        )

    parts = msg.text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        return await msg.reply_text(
            "Welcome Boss To change your Api in your Repository in this format\n\n"
            "/changeapi New Api Here\n\n"
            "Send me I will change it.✨"
        )

    new_api = parts[1].strip()
    PWAPI1 = new_api
    PWAPI2 = new_api
    await msg.reply_text(
        f"✅ **Api Successfully Changed!**\n\n"
        f"🔗 **New Api:**\n`{PWAPI1}`\n\n"
        f"⚡ Change is Live Now — No restart needed! 🚀"
    )



bot.run()
if __name__ == "__main__":
    asyncio.run(main())
