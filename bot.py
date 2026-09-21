import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("شغال 100% ✅")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي اول")
        return
    try:
        ch = ctx.author.voice.channel
        vc = ctx.voice_client or await ch.connect()
        url = "https://stream.radiojar.com/8s5u5tpdtwzuv"
        if vc.is_playing(): vc.stop()
        vc.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await ctx.send("✅ شغال قرآن مكة")
    except Exception as e:
        await ctx.send(f"خطأ: {e}")
        print(e)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
