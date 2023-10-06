import os
import discord
from discord.ui import Button, View, UserSelect, TextInput, Modal
from keep_alive import keep_alive
from discord.ext import commands
from replit import db
import time
from ids import ids_import
import math

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)  # Create a bot object
DISCORD_TOKEN = os.getenv("TOKEN")
print("I'm online")
create_channel_id, bot_role_id, log_channel_id = ids_import()

dbkeys = db.keys()
created_channels = {}
granted_access = {}
if dbkeys:
  for x in dbkeys:
    entire_string = db[x]
    res1 = ''
    idx1 = str(entire_string).index("voice_channel':")
    idx2 = str(entire_string).index(",")
    for idx in range(idx1 + len("voice_channel':") + 1, idx2):
      res1 = res1 + entire_string[idx]
    entire_string = entire_string[entire_string.index(',') + 1:]

    res2 = ''
    idx3 = str(entire_string).index("'member':")
    idx4 = str(entire_string).index(",")
    for idx in range(idx3 + len("'member':") + 1, idx4):
      res2 = res2 + entire_string[idx]
    entire_string = entire_string[entire_string.index(',') + 1:]

    res3 = ''
    idx5 = str(entire_string).index("'message':")
    idx6 = str(entire_string).index(",")
    for idx in range(idx5 + len("'message':") + 1, idx6):
      res3 = res3 + entire_string[idx]
    entire_string = entire_string[entire_string.index(',') + 1:]

    res4 = ''
    idx7 = str(entire_string).index("'last_name_change':")
    idx8 = str(entire_string).index(",")
    for idx in range(idx7 + len("'last_name_change':") + 1, idx8):
      res4 = res4 + entire_string[idx]
    entire_string = entire_string[entire_string.index(',') + 1:]

    res5 = ''
    idx9 = str(entire_string).index("'granted_access': ")
    idx10 = str(entire_string).index("],")
    for idx in range(idx9 + len("'granted_access': ") + 1, idx10):
      res5 = res5 + entire_string[idx]

    created_channels[int(x)] = {
      'voice_channel': int(res1),
      'member': int(res2),
      "message": int(res3),
      'last_name_change': float(res4),
      "granted_access": res5.split(", "),
      'view': None,
      'last_interaction': {}
    }
    granted_access[int(x)] = "Granted Access Users: "
    if created_channels[int(x)]['granted_access'][0] == "":
      created_channels[int(x)]['granted_access'] = []
    else:
      created_channels[int(x)]['granted_access'] = list(
        map(int, created_channels[int(x)]['granted_access']))
print(created_channels)


class PersistentView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Unlock",
                     custom_id="unlock",
                     emoji='🔓')
  async def unlock(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    await button_unlock(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Lock",
                     custom_id="lock",
                     emoji='🔒')
  async def lock(self, interaction: discord.Interaction,
                 button: discord.ui.Button):
    await button_lock(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Visible",
                     custom_id="visible",
                     emoji='👁️')
  async def visible(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    await button_visible(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Invisible",
                     custom_id="invisible",
                     emoji='🕵️')
  async def invisible(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    await button_invisible(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Claim",
                     custom_id="claim",
                     emoji='👑')
  async def claim(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    await button_claim(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Rename Channel",
                     custom_id="rename channel",
                     emoji='✏️')
  async def rename(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    await button_rename_channel(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="User Limit",
                     custom_id="user limit",
                     emoji='🔢')
  async def limit(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    await button_user_limit(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary,
                     label="Channel Invite",
                     custom_id="channel invite",
                     emoji='✉️')
  async def invite(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    await button_channel_invite(interaction)

  @discord.ui.select(cls=UserSelect,
                     placeholder="Grant Private Access",
                     custom_id="Grant Access",
                     min_values=0,
                     max_values=1)
  async def grant(self, interaction: discord.Interaction,
                  select: discord.ui.UserSelect):
    await user_select_grant_access(interaction)

  @discord.ui.select(cls=UserSelect,
                     placeholder="Revoke Private Access",
                     custom_id="Revoke Access",
                     min_values=0,
                     max_values=1)
  async def revoke(self, interaction: discord.Interaction,
                   button: discord.ui.UserSelect):
    await user_select_revoke_access(interaction)


class PersistentViewBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.all()
    intents.message_content = True

    super().__init__(command_prefix=commands.when_mentioned_or('$'),
                     intents=intents)

  async def setup_hook(self) -> None:
    # Register the persistent view for listening here.
    # Note that this does not send the view to any message.
    # In order to do this you need to first send a message with the View, which is shown below.
    # If you have the message_id you can also pass it as a keyword argument, but for this example
    # we don't have one.
    self.add_view(PersistentView())

  async def on_ready(self):
    print(f'Logged in as {self.user} (ID: {self.user.id})')
    print('------')


async def interaction_deletion(interaction):
  if interaction.user.id not in created_channels[
      interaction.channel.id]["last_interaction"]:
    created_channels[interaction.channel.id]["last_interaction"][
      interaction.user.id] = None
  last_interaction = created_channels[
    interaction.channel.id]["last_interaction"][interaction.user.id]
  if last_interaction and last_interaction.is_expired() == False:
    await last_interaction.delete_original_response()
  created_channels[interaction.channel.id]["last_interaction"][
    interaction.user.id] = interaction


bot = PersistentViewBot()


@bot.event
async def on_ready():
  global granted_access

  for x in list(created_channels.keys()):
    fetched_channel = await bot.fetch_channel(x)
    fetched_member = await fetched_channel.guild.fetch_member(
      created_channels[x]['member'])

    db[str(fetched_channel.id)] = str(created_channels[fetched_channel.id])
    for y in created_channels[int(x)]['granted_access']:
      granted_member = await fetched_channel.guild.fetch_member(y)
      granted_access[x] = granted_access[x] + granted_member.mention

    if fetched_channel is not None and fetched_channel.id in created_channels:
      # If the voice channel is empty, delete the voice and text channels
      if len(fetched_channel.members) == 0:
        voice_channel_id = fetched_channel.id
        await fetched_channel.delete()
        del created_channels[voice_channel_id]
        del db[str(voice_channel_id)]

  log_channel = await bot.fetch_channel(log_channel_id)
  message = "I'm ready"
  message = await log_channel.send(message)


@bot.event
async def on_resumed():
  global granted_access

  for x in list(created_channels.keys()):
    fetched_channel = await bot.fetch_channel(x)
    fetched_member = await fetched_channel.guild.fetch_member(
      created_channels[x]['member'])

    db[str(fetched_channel.id)] = str(created_channels[fetched_channel.id])
    for y in created_channels[int(x)]['granted_access']:
      granted_member = await fetched_channel.guild.fetch_member(y)
      granted_access[x] = granted_access[x] + granted_member.mention

    if fetched_channel is not None and fetched_channel.id in created_channels:
      # If the voice channel is empty, delete the voice and text channels
      if len(fetched_channel.members) == 0:
        voice_channel_id = fetched_channel.id
        await fetched_channel.delete()
        del created_channels[voice_channel_id]
        del db[str(voice_channel_id)]

  log_channel = await bot.fetch_channel(log_channel_id)
  message = "I've resumed"
  message = await log_channel.send(message)


@bot.event
async def on_voice_state_update(member, before, after):
  if after.channel is not None and after.channel.id == create_channel_id:
    guild = member.guild
    category = after.channel.category

    # Create a voice channel and a text channel
    if str(member.nick) != 'None':
      voice_channel = await guild.create_voice_channel(
        name=f"{member.nick}'s Channel", category=category)
    else:
            voice_channel = await guild.create_voice_channel(
        name=f"{member.global_name}'s Channel", category=category)

    # Move the member to the new voice channel and set permissions
    await member.move_to(voice_channel)
    await voice_channel.set_permissions(member,
                                        connect=True,
                                        view_channel=True)

    bot_role = voice_channel.guild.get_role(bot_role_id)
    await voice_channel.set_permissions(bot_role,
                                        connect=True,
                                        view_channel=True)

    # Add buttons for making channel public and private

    message = f"Status: 🔓Unlocked and 👁️Visible\nOwner: " + member.mention + "\nChannel Name: " + voice_channel.name + "\nUser Limit: " + str(
      voice_channel.user_limit)
    message = await voice_channel.send(message, view=PersistentView())

    # Store the created voice channel ID and the member ID in a dictionary
    created_channels[voice_channel.id] = {
      "voice_channel": voice_channel.id,
      "member": member.id,
      "message": message.id,
      'last_name_change': 0,
      "granted_access": [member.id],
      "last_interaction": {
        member.id: None
      }
    }
    granted_access[
      voice_channel.id] = "Granted Access Users: " + member.mention
    db[str(voice_channel.id)] = str(created_channels[voice_channel.id])

  if before.channel is not None and before.channel.id in created_channels:
    # If the voice channel is empty, delete the voice and text channels
    if len(before.channel.members) == 0:
      voice_channel_id = before.channel.id
      await before.channel.delete()
      del created_channels[voice_channel_id]
      del db[str(voice_channel_id)]


@bot.command()
async def button_lock(interaction):
  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:

      role_overwrite = voice_channel.overwrites_for(
        interaction.guild.default_role)
      role_overwrite.update(connect=False)
      overwrites = voice_channel.overwrites
      overwrites[interaction.guild.default_role] = role_overwrite

      await voice_channel.edit(overwrites=overwrites)
      await interaction.response.send_message("This channel is now locked!\n" +
                                              granted_access[voice_channel.id],
                                              ephemeral=True,
                                              delete_after=890)

      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace("🔓Unlocked", "🔒Locked")
      await old_message.edit(content=new_message_content)

    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True, delete_after=890)
  else:
    await interaction.response.send_message("You're not in a voice channel!",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def button_unlock(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:

      role_overwrite = voice_channel.overwrites_for(
        interaction.guild.default_role)
      role_overwrite.update(connect=None)
      overwrites = voice_channel.overwrites
      overwrites[interaction.guild.default_role] = role_overwrite
      await voice_channel.edit(overwrites=overwrites)

      await interaction.response.send_message(
        "This channel is now unlocked!\n" + granted_access[voice_channel.id],
        ephemeral=True,
        delete_after=890)
      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace("🔒Locked", "🔓Unlocked")

      await old_message.edit(content=new_message_content)

    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True, delete_after=890)
  else:
    await interaction.response.send_message("You're not in a voice channel!",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def button_invisible(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:

      role_overwrite = voice_channel.overwrites_for(
        interaction.guild.default_role)
      role_overwrite.update(view_channel=False)
      overwrites = voice_channel.overwrites
      overwrites[interaction.guild.default_role] = role_overwrite

      await voice_channel.edit(overwrites=overwrites)
      await interaction.response.send_message(
        "This channel is now invisible!\n" + granted_access[voice_channel.id],
        ephemeral=True,
        delete_after=890)
      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace(
        "👁️Visible", "🕵️Invisible")

      await old_message.edit(content=new_message_content)

    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True, delete_after=890)
  else:
    await interaction.response.send_message("You're not in a voice channel!",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def button_visible(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:

      role_overwrite = voice_channel.overwrites_for(
        interaction.guild.default_role)
      role_overwrite.update(view_channel=None)
      overwrites = voice_channel.overwrites
      overwrites[interaction.guild.default_role] = role_overwrite

      await voice_channel.edit(overwrites=overwrites)
      await interaction.response.send_message(
        "This channel is now visible!\n" + granted_access[voice_channel.id],
        ephemeral=True,
        delete_after=890)
      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace(
        "🕵️Invisible", "👁️Visible")

      await old_message.edit(content=new_message_content)
    else:
      await interaction.response.send_message(
        "You're not in your voice channel!", ephemeral=True, delete_after=890)
  else:
    await interaction.response.send_message("You're not in a voice channel!",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def button_claim(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    fetched_member = await interaction.guild.fetch_member(
      created_channels[voice_channel.id]["member"])
    if fetched_member.voice is None or fetched_member.voice.channel != voice_channel:
      created_channels[voice_channel.id]["member"] = interaction.user.id

      role_overwrite = voice_channel.overwrites_for(interaction.user)
      role_overwrite.update(view_channel=True, connect=True)
      overwrites = voice_channel.overwrites
      overwrites[interaction.user] = role_overwrite
      await voice_channel.edit(overwrites=overwrites)

      if interaction.user.id not in created_channels[
          voice_channel.id]["granted_access"]:
        created_channels[voice_channel.id]["granted_access"].append(
          interaction.user.id)
        granted_access[voice_channel.id] = granted_access[
          voice_channel.id] + interaction.user.mention

      #role_overwrite1 = voice_channel.overwrites_for(fetched_member)
      #role_overwrite1.update(view_channel=None, connect=None)
      #overwrites1 = voice_channel.overwrites
      #overwrites1[fetched_member] = role_overwrite1
      #await voice_channel.edit(overwrites=overwrites1)

      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace(
        str(fetched_member.id), str(interaction.user.id))
      await old_message.edit(content=new_message_content)

      await interaction.response.send_message("This is now your channel",
                                              ephemeral=True,
                                              delete_after=890)
      db[str(voice_channel.id)] = str(created_channels[voice_channel.id])

    else:
      await interaction.response.send_message(
        "The owner of the channel is here", ephemeral=True, delete_after=890)
  else:
    await interaction.response.send_message("You're not in a voice channel",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def user_select_grant_access(interaction):
  if (interaction.data['values']):
    selected_member_id = int(
      list(interaction.data['resolved']['users'].keys())[0])
    selected_member = await interaction.guild.fetch_member(selected_member_id)

    if interaction.user.voice:
      voice_channel = interaction.user.voice.channel
      if interaction.user.id == created_channels[voice_channel.id]["member"]:
        if interaction.user.id != int(selected_member_id):

          role_overwrite = voice_channel.overwrites_for(selected_member)
          role_overwrite.update(view_channel=True, connect=True)
          overwrites = voice_channel.overwrites
          overwrites[selected_member] = role_overwrite
          await voice_channel.edit(overwrites=overwrites)

          if selected_member_id not in created_channels[
              voice_channel.id]["granted_access"]:
            created_channels[voice_channel.id]["granted_access"].append(
              selected_member_id)
            granted_access[voice_channel.id] = granted_access[
              voice_channel.id] + selected_member.mention

            db[str(voice_channel.id)] = str(created_channels[voice_channel.id])
          await interaction.response.send_message(
            "The member granted access\n" + granted_access[voice_channel.id],
            ephemeral=True,
            delete_after=890)
        else:
          await interaction.response.send_message(
            "You cannot change your own permissions\n" +
            granted_access[voice_channel.id],
            ephemeral=True,
            delete_after=890)

      else:
        await interaction.response.send_message(
          "You're not in a voice channel!", ephemeral=True, delete_after=890)
    else:
      await interaction.response.send_message("You're not in a voice channel!",
                                              ephemeral=True,
                                              delete_after=890)
  else:
    await interaction.response.send_message("Please select one",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


@bot.command()
async def user_select_revoke_access(interaction):
  if (interaction.data['values']):
    selected_member_id = int(
      list(interaction.data['resolved']['users'].keys())[0])
    selected_member = await interaction.guild.fetch_member(selected_member_id)

    if interaction.user.voice:
      voice_channel = interaction.user.voice.channel
      if interaction.user.id == created_channels[voice_channel.id]["member"]:
        if interaction.user.id != int(selected_member_id):

          role_overwrite = voice_channel.overwrites_for(selected_member)
          role_overwrite.update(view_channel=None, connect=None)
          overwrites = voice_channel.overwrites
          overwrites[selected_member] = role_overwrite
          await voice_channel.edit(overwrites=overwrites)

          if selected_member_id in created_channels[
              voice_channel.id]["granted_access"]:
            created_channels[voice_channel.id]["granted_access"].remove(
              selected_member_id)
            granted_access[voice_channel.id] = granted_access[
              voice_channel.id].replace(selected_member.mention, '')
            db[str(voice_channel.id)] = str(created_channels[voice_channel.id])

          await interaction.response.send_message(
            "The member denied access\n" + granted_access[voice_channel.id],
            ephemeral=True,
            delete_after=890)
        else:
          await interaction.response.send_message(
            "You cannot change your own permissions\n" +
            granted_access[voice_channel.id],
            ephemeral=True,
            delete_after=890)
      else:
        await interaction.response.send_message(
          "You're not in a voice channel!", ephemeral=True, delete_after=890)
    else:
      await interaction.response.send_message("You're not in a voice channel!",
                                              ephemeral=True,
                                              delete_after=890)
  else:
    await interaction.response.send_message("Please select one",
                                            ephemeral=True,
                                            delete_after=890)

  await interaction_deletion(interaction)


class RenameChannel(Modal, title='Rename Your Channel'):
  answer = TextInput(label='Answer',
                     style=discord.TextStyle.short,
                     min_length=1,
                     max_length=25)

  async def on_submit(self, interaction):

    new_name = str(self.answer)
    old_name = interaction.user.voice.channel.name
    voice_channel = interaction.user.voice.channel
    cooldown_duration = 600  # 10 minutes in seconds
    now = time.time()
    if created_channels[
        voice_channel.id]['last_name_change'] != 0 and now - created_channels[
          voice_channel.id]['last_name_change'] < cooldown_duration:
      await interaction.response.send_message(
        f"You can't change the channel name again so soon.\nYou can do so in: "
        + str(
          math.floor(
            (cooldown_duration -
             (now - created_channels[voice_channel.id]['last_name_change'])) /
            60)) + " minutes and " +
        str(
          math.floor(
            (cooldown_duration -
             (now - created_channels[voice_channel.id]['last_name_change'])) %
            60)) + " seconds.\n" + granted_access[voice_channel.id],
        ephemeral=True,
        delete_after=890)
    else:
      await voice_channel.edit(name=new_name)
      await interaction.response.send_message(
        f'You have renamed your channel to ' + '"' + new_name + '"\n' +
        granted_access[voice_channel.id],
        ephemeral=True,
        delete_after=890)

      old_message = await voice_channel.fetch_message(
        created_channels[voice_channel.id]["message"])
      new_message_content = old_message.content.replace(old_name, new_name)
      await old_message.edit(content=new_message_content)
      created_channels[voice_channel.id]['last_name_change'] = now
      db[str(voice_channel.id)] = str(created_channels[voice_channel.id])

    await interaction_deletion(interaction)


@bot.command()
async def button_rename_channel(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:
      await interaction.response.send_modal(RenameChannel())

    else:
      await interaction.response.send_message(
        f'This is not your voice channel', ephemeral=True, delete_after=890)

      await interaction_deletion(interaction)

  else:
    await interaction.response.send_message(f'You are not in a voice channel',
                                            ephemeral=True,
                                            delete_after=890)
    await interaction_deletion(interaction)


class UserLimit(Modal, title='Limit your channel'):
  answer = TextInput(label='Answer',
                     style=discord.TextStyle.short,
                     min_length=1,
                     max_length=2)

  async def on_submit(self, interaction):
    new_name = str(self.answer)
    old_name = interaction.user.voice.channel.user_limit
    voice_channel = interaction.user.voice.channel
    if new_name.isnumeric():
      if int(new_name) <= 99 or int(new_name) >= 1:
        await voice_channel.edit(user_limit=new_name)
        await interaction.response.send_message(
          f'You have limited the channel to ' + new_name + '\n' +
          granted_access[voice_channel.id],
          ephemeral=True,
          delete_after=890)

        old_message = await voice_channel.fetch_message(
          created_channels[voice_channel.id]["message"])
        new_message_content = old_message.content.replace(
          "User Limit: " + str(int(old_name)),
          "User Limit: " + str(int(new_name)))
        await old_message.edit(content=new_message_content)
    else:
      await interaction.response.send_message(
        f'User limit has to be between 1 to 99',
        ephemeral=True,
        delete_after=890)

    await interaction_deletion(interaction)


@bot.command()
async def button_user_limit(interaction):

  if interaction.user.voice:
    voice_channel = interaction.user.voice.channel
    if interaction.user.id == created_channels[voice_channel.id]["member"]:
      await interaction.response.send_modal(UserLimit())

    else:
      await interaction.response.send_message(
        f'This is not your voice channel', ephemeral=True, delete_after=890)

      await interaction_deletion(interaction)

  else:
    await interaction.response.send_message(f'You are not in a voice channel',
                                            ephemeral=True,
                                            delete_after=890)
    await interaction_deletion(interaction)


@bot.command()
async def button_channel_invite(interaction):
  channel = interaction.channel
  new_invite = await channel.create_invite()
  new_invite_url = new_invite.url
  await interaction.response.send_message(f'Here is your invite:\n' +
                                          new_invite.url,
                                          ephemeral=True,
                                          delete_after=890)

  await interaction_deletion(interaction)


keep_alive()
bot.run(DISCORD_TOKEN)
