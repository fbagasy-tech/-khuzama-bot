import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# جربنا 3 روابط لخزامى - واحد منهم بيشتغل
STREAMS = {
    "خزامى 1": "https://stream.radiojar.com/4wqre23um86uv",
    "خزامى 2": "https://l1.m2.sba.sa/live/7/playlist.m3u8", # الرابط الرسمي من موقع SBA
    "نداء": "https://stream.radiojar.com/8s5u5tpdtwzuv",
}

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")

@bot.command()
async def join(ctx, num: int = 2):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي")
        return

    ch = ctx.author.voice.channel
    vc = ctx.voice_client or await ch.connect()

    # اختار الرابط
    key = list(STREAMS.keys())[num-1] if 1 <= num <= 3 else "خزامى 2"
    url = STREAMS[key]

    if vc.is_playing(): vc.stop()

    def after(e):
        print(f"After play error: {e}")

    try:
        # نستخدم Opus بدل PCM - يشتغل احسن في Railway
        source = await discord.FFmpegOpusAudio.from_probe(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn')
        vc.play(source, after=after)
        await ctx.send(f"✅ جربت: {key}\nالرابط: {url}\nاذا ما سمعت صوت، جرب `!join 1` ثم `!join 3`")
    except Exception as e:
        await ctx.send(f"❌ خطأ: {e}")
        print(e)

@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
