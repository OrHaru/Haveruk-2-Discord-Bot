import os
import discord
from discord.ui import Button, View
from keep_alive import keep_alive
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)  # Create a bot object
DISCORD_TOKEN = os.getenv("TOKEN")

created_channels = {}


@bot.event
async def on_voice_state_update(member, before, after):
  if after.channel is not None and after.channel.id == 1083156473087013054:
    guild = member.guild
    category = after.channel.category

    # Create a voice channel and a text channel
    voice_channel = await guild.create_voice_channel(
      name=f"{member.display_name}'s Channel", category=category)
    text_channel = await guild.create_text_channel(
      name=f"{member.display_name}'s Channel", category=category)

    # Move the member to the new voice channel and set permissions
    await member.move_to(voice_channel)
    await voice_channel.set_permissions(member,
                                        manage_channels=True,
                                        manage_roles=True)
    await text_channel.set_permissions(member,
                                       manage_channels=True,
                                       manage_roles=True)
    print(created_channels)
    message = f"Welcome to your new channel, {member.mention}!"
    await text_channel.send(message)
    # Store the created voice channel ID and the member ID in a dictionary
    created_channels[voice_channel.id] = {
      "voice_channel": voice_channel,
      "text_channel": text_channel,
      "member_id": member.id
    }

  if before.channel is not None and before.channel.id in created_channels:
    # If the voice channel is empty, delete the voice and text channels
    if len(before.channel.members) == 0:
      voice_channel_id = before.channel.id
      text_channel = created_channels[voice_channel_id]["text_channel"]
      await before.channel.delete()
      await text_channel.delete()
      del created_channels[voice_channel_id]

bot.run(DISCORD_TOKEN)
