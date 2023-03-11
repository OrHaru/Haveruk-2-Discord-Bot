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
                                        connect = True, view_channel = True)
    await text_channel.set_permissions(member,
                                       view_channel = True)

    # Add buttons for making channel public and private
    unlock_button = Button(style=discord.ButtonStyle.green,
                           label="Unlock",
                           custom_id="unlock")
    lock_button = Button(style=discord.ButtonStyle.red,
                         label="Lock",
                         custom_id="lock")
    visible_button = Button(style=discord.ButtonStyle.red,
                         label="Visible",
                         custom_id="visible")
    invisible_button = Button(style=discord.ButtonStyle.red,
                         label="Invisible",
                         custom_id="invisible")
    view = View()
    view.add_item(unlock_button)
    view.add_item(lock_button)
    view.add_item(visible_button)
    view.add_item(invisible_button)
    unlock_button.callback = button_unlock
    lock_button.callback = button_lock
    visible_button.callback = button_visible
    invisible_button.callback = button_invisible

    message = f"Welcome to your new channel, {member.mention}!"
    message = await text_channel.send(message, view=view)

    # Store the created voice channel ID and the member ID in a dictionary
    created_channels[voice_channel.id] = {
      "voice_channel": voice_channel,
      "text_channel": text_channel,
      "member_id": member.id,
      "view": view,
      "message": message
    }
  if before.channel is not None and before.channel.id in created_channels:
    # If the voice channel is empty, delete the voice and text channels
    if len(before.channel.members) == 0:
      voice_channel_id = before.channel.id
      text_channel = created_channels[voice_channel_id]["text_channel"]
      await before.channel.delete()
      await text_channel.delete()
      del created_channels[voice_channel_id]


@bot.command()
async def button_lock(interaction):
  if interaction.user.voice:
    channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[channel.id]["member_id"]:
      overwrites = {
        interaction.guild.default_role:
        discord.PermissionOverwrite(connect=False),
        interaction.user:
        discord.PermissionOverwrite(connect = True, view_channel = True),
        bot.user:
        discord.PermissionOverwrite(connect=True)
      }
      await channel.edit(overwrites=overwrites)
      await interaction.response.send_message("This channel is now locked!",
                                              ephemeral=True)
    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True)


@bot.command()
async def button_unlock(interaction):
  if interaction.user.voice:
    channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[channel.id]["member_id"]:

      overwrites = {
        interaction.guild.default_role:
        discord.PermissionOverwrite(connect=True),
        interaction.user:
        discord.PermissionOverwrite(connect = True, view_channel = True),
        bot.user:
        discord.PermissionOverwrite(connect=True)
      }
      await channel.edit(overwrites=overwrites)
      await interaction.response.send_message("This channel is now unlocked!",
                                              ephemeral=True)
    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True)


@bot.command()
async def button_invisible(interaction):
  if interaction.user.voice:
    channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[channel.id]["member_id"]:

      overwrites = {
        interaction.guild.default_role:
        discord.PermissionOverwrite(view_channel = False),
        interaction.user:
        discord.PermissionOverwrite(connect = True, view_channel = True),
        bot.user:
        discord.PermissionOverwrite(connect=True)
      }
      await channel.edit(overwrites=overwrites)
      await interaction.response.send_message("This channel is now invisible!",
                                              ephemeral=True)
    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True)


@bot.command()
async def button_visible(interaction):
  if interaction.user.voice:
    channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[channel.id]["member_id"]:

      overwrites = {
        interaction.guild.default_role:
        discord.PermissionOverwrite(view_channel = True),
        interaction.user:
        discord.PermissionOverwrite(connect = True, view_channel = True),
        bot.user:
        discord.PermissionOverwrite(connect=True)
      }
      await channel.edit(overwrites=overwrites)
      await interaction.response.send_message("This channel is now visible!",
                                              ephemeral=True)
    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True)

keep_alive()
bot.run(DISCORD_TOKEN)
