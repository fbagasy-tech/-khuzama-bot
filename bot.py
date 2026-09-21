import discord
from discord.ext import commands
import yt_dlp
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}

@bot.event
async def on_ready():
    print(f"شغال: {bot.user} - 24/7 جاهز")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("دخلت ✅")

@bot.command()
async def play(ctx, *, url):
    if "/live/" in url:
        url = url.replace("/live/", "/watch?v=").split("?")[0].split("&")[0]
        url = url.split("?si=")[0]
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("ادخل روم صوتي اول!")
            return
    await ctx.send(f"🔍 جاري التشغيل: {url}")
    with yt_dlp.YoutubeDL(YDL) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: info = info['entries'][0]
            link = info['url']
            title = info.get('title','مقطع')
        except Exception as e:
            await ctx.send(f"ما قدرت اشغل: {e}")
            return
    src = await discord.FFmpegOpusAudio.from_probe(link, **FFMPEG)
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(src)
    await ctx.send(f"▶️ الآن: **{title}** - شغال 24/7")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت ⏹️")

@bot.command()
async def alekhwa(ctx):
    guild = ctx.guild
    cat = await guild.create_category("・ الاخوه ・")
    vc1 = await guild.create_voice_channel("・ مجلس الاخوه — 100", category=cat)
    await vc1.edit(user_limit=0)
    vc2 = await guild.create_voice_channel("・ قران و اغاني — 24/7", category=cat)
    await guild.create_text_channel("・ سوالف الاخوه", category=cat)
    await ctx.send("تم انشاء مجلس الاخوه ✅ استخدم !join و !play")

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("حط التوكن في متغير البيئة DISCORD_TOKEN")
else:
    bot.run(token)
