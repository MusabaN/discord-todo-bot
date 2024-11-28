import discord
from discord import app_commands
from todo_list import TodoList
from dotenv import load_dotenv
from image_to_event_url import create_event_url
import requests
import os

class TodoBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.todo_lists = {}  # Dictionary to store TodoList objects for each thread

    async def setup_hook(self):
        await self.tree.sync()

client = TodoBot()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_message(message):
    # Check if the message was sent to the "test" channel (either by name or ID)
    if message.channel.name != "bandrom-booking":
        return  # Do nothing if the message is not in the "test" channel
    # Check if the message has attachments and avoid responding to the bot itself
    if message.attachments and not message.author.bot:
        for attachment in message.attachments:
            # Get the URL of the attachment
            image_url = attachment.url

            # Download the image using requests
            response = requests.get(image_url)
            if response.status_code == 200:
                # Save the image temporarily to process it
                image_path = 'temp_image.jpg'
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # Pass the image to your function to generate the event URL
                try:
                    event_url = create_event_url(image_path)
                except Exception as e:
                    await message.channel.send(f"IKKE BRA NOK SKJERMBILDE")
                    os.remove(image_path)
                    return
                
                # Send the event URL as a response directly to the person who sent the image
                await message.channel.send(f"{message.author.mention} Her er event-url'en din: {event_url}")
                
                # Delete the temporary image file after processing
                os.remove(image_path)

@client.event
async def on_thread_create(thread):
    # Tag all members of the server in the first message
    members = thread.guild.members
    members_str = " ".join([member.mention for member in members if not member.bot])
    await thread.send(f"Yo {members_str}")

    if thread.parent.name.lower() == 'demos':
        todo_list = TodoList()
        client.todo_lists[thread.id] = todo_list
        await thread.send(str(todo_list))

async def get_todo_list(interaction: discord.Interaction) -> tuple[TodoList, discord.Message] | None:
    if not isinstance(interaction.channel, discord.Thread) or interaction.channel.parent.name.lower() != 'demos':
        await interaction.response.send_message("This command can only be used in a thread in the 'demos' channel.", ephemeral=True)
        return None

    todo_list_message = await find_todo_list_message(interaction.channel)
    if todo_list_message is None:
        await interaction.response.send_message("Couldn't find the todo list message. Please recreate the thread.", ephemeral=True)
        return None

    todo_list = TodoList.parse_message(todo_list_message.content)
    return todo_list, todo_list_message

async def find_todo_list_message(channel):
    async for message in channel.history(limit=4, oldest_first=True):
        if message.author == client.user and "**Todo liste:**" in message.content:
            return message
    return None

@client.tree.command()
async def add(interaction: discord.Interaction, task: str):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result
    task_with_user = f"{task} ({interaction.user.name})"
    todo_list.add_todo_item(task_with_user)

    await todo_list_message.edit(content=str(todo_list))
    await interaction.response.send_message(f"Added task: {task_with_user}", ephemeral=True)
    

@client.tree.command()
async def done(interaction: discord.Interaction, item_number: int):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    try:
        todo_list.complete_todo_item(item_number)  # The TodoList class handles 1-based indexing
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Marked item {item_number} as done.", ephemeral=True)
    except IndexError:
        await interaction.response.send_message(f"Error: Item {item_number} does not exist in the todo list.", ephemeral=True)
    

@client.tree.command()
async def undo(interaction: discord.Interaction, item_number: int):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    try:
        todo_list.undo_done_item(item_number)  # The TodoList class handles 1-based indexing
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Moved item {item_number} back to the todo list.", ephemeral=True)
    except IndexError:
        await interaction.response.send_message(f"Error: Item {item_number} does not exist in the done list.", ephemeral=True)

@client.tree.command()
async def delete_todo_item(interaction: discord.Interaction, item_number: int):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    try:
        todo_list.delete_todo_item(item_number)  # The TodoList class handles 1-based indexing
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Deleted item {item_number} from the todo list.", ephemeral=True)
    except IndexError:
        await interaction.response.send_message(f"Error: Item {item_number} does not exist in the todo list.", ephemeral=True)

@client.tree.command()
async def delete_done(interaction: discord.Interaction, item_number: int):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result
    
    try:
        todo_list.delete_completed_item(item_number)  # The TodoList class handles 1-based indexing
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Deleted item {item_number} from the done list.", ephemeral=True)
    except IndexError:
        await interaction.response.send_message(f"Error: Item {item_number} does not exist in the done list.", ephemeral=True)

@client.tree.command()
async def delete_all_done(interaction: discord.Interaction):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    todo_list.delete_all_completed_items()
    await todo_list_message.edit(content=str(todo_list))
    await interaction.response.send_message("Deleted all items from the done list.", ephemeral=True)

@client.tree.command()
async def demo(interaction: discord.Interaction, link: str):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    try:
        todo_list.set_demo_link(link)
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Added demo link: {link}", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Error: Invalid demo link.", ephemeral=True)

@client.tree.command()
async def lyrics(interaction: discord.Interaction, link: str):
    result = await get_todo_list(interaction)
    if result is None:
        return

    todo_list, todo_list_message = result

    try:
        todo_list.set_lyrics_link(link)
        await todo_list_message.edit(content=str(todo_list))
        await interaction.response.send_message(f"Added lyrics link: {link}", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Error: Invalid lyrics link.", ephemeral=True)


load_dotenv('.env')
discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)