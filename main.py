#main.py
'''This code is for running discord bot for save photo on construction line check 
  1.create folder YYMMDD for each day the photo was sent
  2.rename photo to YYmmddhhmm_caption and save for the folder in that day ss'''

######################################################################################################################
import discord
from dotenv import load_dotenv
import os
import requests
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz
import asyncio
from system_stats import get_cpu_temp, get_power_status, get_cpu_usage, get_ram_usage



### for get token and webhook from powerautomate ###
load_dotenv()
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

### Channel to listen ###
allowed_channels = [1379111305700573335, 1379114811589394472]  # Replace with your channel IDs


### Listen for message in discord ###
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

### Set up flask for web server ###
app = Flask('')
@app.route('/')
def home():
    return "🤖 Discord bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8081)

# Run Flask server in background
Thread(target=run).start()

### 1/4 hourly notif  ###
async def hourly_notify():
    await client.wait_until_ready()
    channel = client.get_channel(1379114811589394472)  # Replace with your real channel ID (as an integer)
    while not client.is_closed():
        if channel:
            temp = get_cpu_temp()
            power = get_power_status()
            cpu = get_cpu_usage()
            ram = get_ram_usage()
            await channel.send(f"🟢 Bot heartbeat: online and running!\n"
                f"🌡️ CPU Temp: {temp}°C\n"
                f"{power}\n"
                f"🖥️ CPU Usage: {cpu}%\n"
                f"🧠 RAM Usage: {ram}%"
                )
        await asyncio.sleep(900)  # Wait 1 hour (3600 seconds)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    if not hasattr(client, 'heartbeat_task_started'):
        client.heartbeat_task_started = True
        asyncio.create_task(hourly_notify())




### listen message ####

@client.event
async def on_message(message):
    print(f"[LOG] New message from {message.author}: {message.content}")

    if message.content.strip() == "!status":
        await message.channel.send(f"✅ I’m alive as {client.user}\n Please send me a photo to save it.\n"f"🌡️ CPU Temp: {temp}°C")
        return

    if message.author.bot:
        print("[LOG] Ignored bot message")
        return

    # ⏰ Restrict to 08:00–22:00 Thai time
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    '''if now.hour < 6 or now.hour >= 23.59:
        print("[LOG] Outside active hours. Ignoring message.")
        return'''

    ### Protect no attachement  ###
    if not message.attachments:
        print("[LOG] Message received without attachment. Skipping.")
        return

    if message.channel.id not in allowed_channels:
        print("[LOG] Message not in allowed channel. Ignoring.")
        return  # Ignore messages from other channels

    print(f"[LOG] {len(message.attachments)} attachment(s) found")
    caption = message.content.strip().replace("/", "_") or "no_caption"
    timestamp = now.strftime("%y%m%d")
    folder_name = now.strftime("%Y%m%d")
    attachments = message.attachments

    ### If 1 filename   ###
    if len(attachments) == 1:
        attachment = attachments[0]
        filename = f"{timestamp}_{caption}"
        filename += ".jpg"  # Default to .jpg if no valid extension exists

        print(f"[LOG] Sending file: {filename}")

        data = {
            "filename": attachment.filename,
            "url": attachment.url,
            "author": str(message.author),
            "channel": str(message.channel),
            "folder": folder_name,
            "renamed": filename,
            "caption": caption
        }

        try:
            res = requests.post(WEBHOOK_URL, json=data)
            print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
            if res.status_code == 200 or 202:
                await message.channel.send(f"✅ File `{filename}` was already uploaded")
            else:
                await message.channel.send(f"❌ Failed to upload `{filename}`")
        except Exception as e:
            print(f"[ERROR] Failed to send to Pipedream: {e}")
            await message.channel.send(f"❌ Upload error: {e}")

    ### Else More than 1 files  ###
    else:
        for i, attachment in enumerate(attachments, start=1):
            indexed_caption = f"{caption}_{i}"
            filename = f"{timestamp}_{caption}_{i}"
            filename += ".jpg"  # Default to .jpg if no valid extension exists
            print(f"[LOG] Sending file: {filename}")

            data = {
                "filename": attachment.filename,
                "url": attachment.url,
                "author": str(message.author),
                "channel": str(message.channel),
                "folder": folder_name,
                "renamed": filename,
                "caption": indexed_caption
            }

            try:
                res = requests.post(WEBHOOK_URL, json=data)
                print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
                if res.status_code == 200 or 202 :
                    await message.channel.send(f"✅ File `{filename}` was already uploaded")
                else:
                    await message.channel.send(f"❌ Failed to upload `{filename}`")
            except Exception as e:
                print(f"[ERROR] Failed to send to Pipedream: {e}")
                await message.channel.send(f"❌ Upload error: {e}")

client.run(TOKEN)
