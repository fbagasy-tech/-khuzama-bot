import discord
from discord.ext import commands
import os
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")

@bot.command()
async def join(ctx):
    if not ctx.author.voice: return await ctx.send("ادخل روم")
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()
    # رابط قرآن مكة مضمون 100%
    url = "https://stream.radiojar.com/8s5u5tpdtwzuv"
    vc.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
    await ctx.send("✅ شغال قرآن مكة")

@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
