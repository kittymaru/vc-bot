import discord
import asyncpg
from dotenv import load_dotenv
from discord.sinks import WaveSink
import os
import random

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

    # create/check if database exists
    await db.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print(f"{bot.user} online")

# test slash command
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def hello(ctx):
    await ctx.respond("Hello!")

# print database (for testing)
# TODO: change to write to txt file for unlimited message length
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

# join voice channel user is in
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def join(ctx):
    # user is not in vc
    if not ctx.author.voice:
        await ctx.respond("Join a voice channel first!")
        return
    
    # bot already in vc
    if ctx.guild.voice_client:
        await ctx.respond("I'm already connected to a voice channel!")
        return
    
    await ctx.respond("Joined voice channel successfully!")
    await ctx.author.voice.channel.connect()

# leave voice channel user is in
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def leave(ctx):
    # check if in vc
    if not ctx.guild.voice_client:
        await ctx.respond("I'm not connected to a voice channel!")
        return
    
    await ctx.respond("Left voice channel successfully!")
    await ctx.guild.voice_client.disconnect()

# start recording
@bot.slash_command(guild_ids=[os.getenv("GUILD_ID")])
async def record(ctx):
    # check if in vc
    if not ctx.guild.voice_client:
        await ctx.respond("I'm not connected to a voice channel!")
        return

    # check if recording
    if ctx.guild.voice_client.is_recording():
        await ctx.respond("I'm already recording!")
        return
    
    # make sink
    sink = WaveSink()

    # begin recording
    await ctx.respond("Recording started!")
    ctx.guild.voice_client.start_recording(sink, record_callback, ctx)

def record_callback(sink, ctx):
    # make new folder with unique identifier in recordings
    session_id = f"{ctx.guild.id}_{random.randint(100000, 999999)}"
    base_path = f"recordings/{session_id}"
    os.makedirs(base_path, exist_ok=True)

    for user_id, audio in sink.audio_data.items():
        filename = f"{base_path}/{user_id}.wav"

        with open(filename, "wb") as file:
            file.write(audio.file.read())

        print(f"Saved recording for {user_id} in local storage")
    

# stop recording, send transcript as txt file

# end
@bot.event
async def on_close():
    # close database
    if db:
        await db.close()

bot.run(BOT_TOKEN)
