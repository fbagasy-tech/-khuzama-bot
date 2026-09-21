import discord
from discord.ext import commands, tasks
import os, asyncio, aiohttp
from datetime import datetime
import pytz

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

TIMEZONE = pytz.timezone("Asia/Riyadh")
RADIO_KHUZAMA = "https://radioplus.sba.sa/live/7"
RADIO_NIDAA = "https://radioplus.sba.sa/live/1"
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
last_event = None
is_switching = False

ALLOWED_NAMES = ["اذاعة خزامة", "راديو خزامة", "خزامة"]

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if vc.name.strip().lower() in [n.lower() for n in ALLOWED_NAMES]:
                try:
                    conn = await vc.connect()
                    conn.play(discord.FFmpegPCMAudio(RADIO_KHUZAMA, **FFMPEG_OPTS))
                    break
                except: pass
    check_prayer.start()
    keep_alive.start()

@tasks.loop(minutes=1)
async def check_prayer():
    global last_event, is_switching
    if is_switching: return
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Riyadh&country=Saudi%20Arabia&method=4") as r:
                data = await r.json()
                timings = data['data']['timings']
                now = datetime.now(TIMEZONE)
                cur = now.strftime("%H:%M")
                today = now.strftime("%Y-%m-%d")
                for en in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
                    if timings[en] == cur and last_event!= f"{today}-{en}":
                        last_event = f"{today}-{en}"
                        is_switching = True
                        for g in bot.guilds:
                            vc = g.voice_client
                            if vc:
                                if vc.is_playing(): vc.stop()
                                vc.play(discord.FFmpegPCMAudio(RADIO_NIDAA, **FFMPEG_OPTS))
                                await asyncio.sleep(600)
                                if vc.is_playing(): vc.stop()
                                vc.play(discord.FFmpegPCMAudio(RADIO_KHUZAMA, **FFMPEG_OPTS))
                        is_switching = False
                        break
    except: is_switching = False

@tasks.loop(minutes=5)
async def keep_alive():
    for g in bot.guilds:
        vc = g.voice_client
        if vc and not vc.is_playing() and not is_switching:
            vc.play(discord.FFmpegPCMAudio(RADIO_KHUZAMA, **FFMPEG_OPTS))

bot.run(os.getenv("TOKEN"))
