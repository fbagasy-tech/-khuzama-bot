import discord, re, aiohttp, datetime, pytz, os, asyncio
from discord.ext import commands, tasks

KSA = pytz.timezone('Asia/Riyadh')
times = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

QURAN = "https://stream.radiojar.com/8s5u5tpdtwzuv"
PAGE = "https://radioplus.sba.sa/live/7"
FFMPEG = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -user_agent "Mozilla/5.0"', 'options': '-vn'}

last_channel = None

async def get_hls():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(PAGE, headers={"User-Agent":"Mozilla/5.0"}, timeout=20) as r:
                html = await r.text()
                m = re.findall(r'https://[^"\']+\.m3u8[^"\']*', html)
                if m:
                    return m[0].replace('\\u002F','/').replace('\\','')
    except: pass
    return None

def get_url():
    return QURAN # نثبت قرآن لين نحل حجب SBA - خزامى يرجع لما ننقل السيرفر للسعودية

async def update_times():
    global times
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Makkah&country=Saudi Arabia&method=4") as r:
                j = await r.json()
                times = j['data']['timings']
    except: pass

@tasks.loop(seconds=30)
async def checker():
    global last_channel
    if not last_channel: return
    try:
        guild = last_channel.guild
        vc = guild.voice_client
        if not vc or not vc.is_connected():
            print("Reconnecting...")
            vc = await last_channel.connect()

        if not vc.is_playing():
            print("Re-playing...")
            url = await get_hls()
            if not url: url = QURAN
            vc.play(discord.FFmpegPCMAudio(url, **FFMPEG), after=lambda e: print(f"Player error: {e}"))
            vc.current_url = url
    except Exception as e:
        print(f"Checker error: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency*1000)}ms")

@bot.command()
async def join(ctx):
    global last_channel
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي")
        return
    last_channel = ctx.author.voice.channel
    vc = ctx.voice_client
    if not vc:
        vc = await last_channel.connect()
    elif vc.channel!= last_channel:
        await vc.move_to(last_channel)

    if vc.is_playing(): vc.stop()

    url = await get_hls()
    if not url:
        await ctx.send("⚠️ خزامى محجوب من Railway أمريكا، شغلت قرآن مؤقتاً - البوت بيبقى في الروم ما بيطلع")
        url = QURAN

    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG), after=lambda e: print(f"Player ended: {e}"))
    await ctx.send(f"✅ دخلت وما راح أطلع من حالي - شغال: {url[:50]}")
    if not checker.is_running():
        checker.start()

@bot.command()
async def leave(ctx):
    global last_channel
    last_channel = None
    checker.stop()
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت")

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    await update_times()

bot.run(os.getenv("DISCORD_TOKEN"))
