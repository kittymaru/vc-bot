import discord
from dotenv import load_dotenv
import os

# Get token
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('chuuya'):
        await message.channel.send('i hate chuuya bro')

client.run(BOT_TOKEN)