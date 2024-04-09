import discord
from discord.ext import tasks, commands
import datetime
import pytz
import requests
import re
import os
from datetime import datetime

ai_backend = 'cloudflare image ai backend'
token = 'discord bot token'
secret_key = 'secret key for the image ai backend'
channel_id = 'channel id used for daily message'

# Initialize a dictionary for logging user requests
user_requests = {}

# Replace 'your_token_here' with your Discord bot token
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@tasks.loop(minutes=1)
async def daily_message():
    now = datetime.now(pytz.timezone('Europe/Berlin'))
    if now.hour == 17 and now.minute == 0:  # Check if it's 17:00
        channel = bot.get_channel(channel_id)  # Replace YOUR_CHANNEL_ID with the actual channel ID
        await channel.send("@everyone kommt cs2 ihr pisser")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    daily_message.start()  # Start the daily message task

@bot.event
async def on_message(message):
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return

    # Determine if the message is a DM or a server message
    if isinstance(message.channel, discord.DMChannel):
        # This is a DM
        content = message.content.strip()
    else:
        # This is a server message, check if the bot is mentioned
        if bot.user.mentioned_in(message):
            content = re.sub(r'<@!?{0}>'.format(bot.user.id), '', message.content).strip()
        else:
            # If the bot isn't mentioned in a server message, ignore the message
            return

    # From here on, 'content' is used which is independent of the message source (DM or server)
    parts = content.split(';')
    prompt = parts[0].strip()
    num_images = 1  # Default number of images

    # If a number of images is specified, try to parse it
    if len(parts) > 1:
        try:
            num_images = int(parts[1].strip())
        except ValueError:
            # Adjust the response based on context (DM or server)
            response = "Couldn't understand the number of images, defaulting to 1."
            if isinstance(message.channel, discord.DMChannel):
                await message.channel.send(response)
            else:
                await message.channel.send(f"{message.author.mention} {response}")
            num_images = 1

    # Notify the user that the image(s) is/are being generated
    await message.channel.send(f'{message.author.mention} Generating {num_images} image(s) for prompt: "{prompt}"...')
    
    user_folder = os.path.join('user_images', str(message.author).replace('#', '_'))  # Replace '#' with '_' to avoid path issues
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    for _ in range(num_images):
        # Your backend server URL
        url = ai_backend
        
        # Headers including the secret key
        headers = {
            'Content-Type': 'application/json',
            'X-Secret-Key': secret_key
        }
        
        # Data to be sent to your backend
        data = {'prompt': prompt}
        
        # Make a POST request to the backend
        response = requests.post(url, json=data, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Format the current date and time to use in the file name
            timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            image_filename = f"{timestamp}.png"
            prompt_filename = f"{timestamp}.txt"

            # Assuming the response is an image, save it
            with open(os.path.join(user_folder, image_filename), 'wb') as f:
                f.write(response.content)
            
            # Save the prompt used
            with open(os.path.join(user_folder, prompt_filename), 'w') as f:
                f.write(prompt)
            
            # Send the image back to the channel with a mention to the user
            await message.channel.send(f'{message.author.mention} Prompt: "{prompt}"', file=discord.File(os.path.join(user_folder, image_filename)))
        else:
            # If something went wrong, notify the user
            await message.channel.send(f'Sorry {message.author.mention}, something went wrong generating image {_+1}.')
            break  # Exit the loop if an error occurs

    # Make sure to process commands if any
    await bot.process_commands(message)

# Start the bot
bot.run(token)
