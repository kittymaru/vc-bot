import discord
import asyncpg
from dotenv import load_dotenv
import os

# Get token
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

bot = discord.Bot()
db = None

# start
@bot.event
async def on_ready():
    global db
    db = await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST")
    )

    # create/check if table exists
    await db.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print(f"We have logged in as {bot.user}")

# test slash command
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def hello(ctx):
    await ctx.respond("Hello!")

# print database (for testing)
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def printdatabase(ctx):
    rows = await db.fetch(
        """
        SELECT user_id, guild_id, text, created_at
        FROM transcriptions
        ORDER BY created_at DESC
        LIMIT 10
        """
    )

    if not rows:
        await ctx.respond("Database is empty.")
        return

    message = ""
    for row in rows:
        message += (
            f"User: {row['user_id']}\n"
            f"Guild: {row['guild_id']}\n"
            f"Text: {row['text']}\n"
            f"Time: {row['created_at']}\n"
            f"---\n"
        )

    # Discord message limit safety
    if len(message) > 1900:
        message = message[:1900] + "\n...(truncated)"

    await ctx.respond(f"```\n{message}\n```")

# end
@bot.event
async def on_close():
    # close database
    if db:
        await db.close()

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