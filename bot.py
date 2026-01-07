import discord
from dotenv import load_dotenv
import os

# Get token
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command()
async def hello(ctx):
    await ctx.respond("Hello!")

bot.run(BOT_TOKEN)

# intents = discord.Intents.default()
# intents.message_content = True

# client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     print(f'We have logged in as {client.user}')

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
    
#     if message.content.startswith('chuuya'):
#         await message.channel.send('i hate chuuya bro')
#     elif message.content.startswith('sans'):
#         await message.channel.send('megalovania')

# client.run(BOT_TOKEN)