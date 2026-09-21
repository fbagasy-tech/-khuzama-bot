import discord, re, asyncio, aiohttp, datetime, pytz
from discord.ext import commands, tasks

KSA = pytz.timezone('Asia/Riyadh')
times = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

QURAN = "https://stream.radiojar.com/8s5u5tpdtwzuv"
OFFICIAL_PAGE = "https://radioplus.sba.sa/live/7"
FFMPEG = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -user_agent "Mozilla/5.0"', 'options': '-vn'}

async def get_khuzama_stream():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(OFFICIAL_PAGE, headers={"User-Agent":"Mozilla/5.0"}, timeout=15) as r:
                txt = await r.text()
                m = re.search(r'https://[^"\']+\.m3u8[^"\']*', txt)
                if m:
                    url = m.group(0).replace('\\u002F','/').replace('\\','')
                    print(f"Found khuzama: {url}")
                    return url
    except Exception as e:
        print(f"Khuzama extract error: {e}")
    # اذا انحظر من امريكا - fallback مؤقت لين ننقل السيرفر للسعودية
    return QURAN

async def update_times():
    global times
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Makkah&country=Saudi Arabia&method=4") as r:
                j = await r.json()
                times = j['data']['timings']
    except: pass

def is_prayer_time():
    now = datetime.datetime.now(KSA)
    if now.weekday()==4 and 11 <= now.hour < 14:
        return True
    for p in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
        if p in times:
            try:
                hh,mm = map(int, times[p].split()[0].split(':'))
                pt = now.replace(hour=hh, minute=mm, second=0)
                if pt <= now < pt + datetime.timedelta(minutes=25):
                    return True
            except: pass
    return False

def play(vc, url):
    vc.current_url = url
    vc.play(discord.FFmpegOpusAudio.from_probe(url, **FFMPEG))

@tasks.loop(minutes=1)
async def checker():
    for vc in bot.voice_clients:
        try:
            should_quran = is_prayer_time()
            target = QURAN if should_quran else await get_khuzama_stream()
            if getattr(vc,'current_url',None)!=target or not vc.is_playing():
                vc.stop()
                play(vc, target)
        except Exception as e:
            print(e)

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    await update_times()
    checker.start()

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم")
        return
    ch = ctx.author.voice.channel
    vc = ctx.voice_client or await ch.connect()
    if ctx.guild.voice_client and vc.channel!=ch:
        await vc.move_to(ch)
    if vc.is_playing(): vc.stop()

    url = QURAN if is_prayer_time() else await get_khuzama_stream()
    try:
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG)
        vc.play(source)
        vc.current_url = url
        if url==QURAN and is_prayer_time():
            await ctx.send("✅ شغال: نداء الإسلام 🕋")
        else:
            await ctx.send("✅ شغال: خزامى طرب 24 ساعة 🎵 - بث رسمي مباشر")
    except Exception as e:
        await ctx.send(f"❌ {e}")
        print(e)

@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(__import__('os').getenv("DISCORD_TOKEN"))
