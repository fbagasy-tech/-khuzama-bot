import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")

@bot.command()
async def alekhwa(ctx):
    guild = ctx.guild
    cat = await guild.create_category("•  الاخوة  •")
    vc1 = await guild.create_voice_channel("•  مجلس الاخوة - 100  •", category=cat)
    await vc1.edit(user_limit=0)
    vc2 = await guild.create_voice_channel("•  قرآن و اغاني - 24/7  •", category=cat)
    await guild.create_text_channel("•  سوالف الاخوة  •", category=cat)
    await ctx.send("تم انشاء مجلس الاخوة ✅ استخدم !join و !play")

@bot.command(name="join")
async def join_cmd(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"دخلت {channel}")
    else:
        await ctx.send("ادخل روم صوتي اول")

@bot.command(name="leave")
async def leave_cmd(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ طلعت من محطة خزامي")
    else:
        await ctx.send("انا مو داخل الروم اصلا")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت ✅")
    else:
        await ctx.send("مو داخل روم")

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("حط التوكن في متغير البيئة DISCORD_TOKEN")
else:
    bot.run(token)
