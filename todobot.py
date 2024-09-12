import discord
from discord import app_commands
from todo_list import TodoList
from dotenv import load_dotenv
import os

class TodoBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.todo_lists = {}  # Dictionary to store TodoList objects for each thread

    async def setup_hook(self):
        await self.tree.sync()

client = TodoBot()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_thread_create(thread):
    if thread.parent.name.lower() == 'demos':
        todo_list = TodoList()
        client.todo_lists[thread.id] = todo_list
        await thread.send(str(todo_list))

async def find_todo_list_message(channel):
    async for message in channel.history(limit=100):
        if message.author == client.user and "**Todo liste:**" in message.content:
            return message
    return None

@client.tree.command()
async def add(interaction: discord.Interaction, task: str):
    if not isinstance(interaction.channel, discord.Thread) or interaction.channel.parent.name.lower() != 'demos':
        await interaction.response.send_message("This command can only be used in a thread in the 'demos' channel.", ephemeral=True)
        return

    todo_list_message = await find_todo_list_message(interaction.channel)
    if todo_list_message is None:
        await interaction.response.send_message("Couldn't find the todo list message. Please recreate the thread.", ephemeral=True)
        return

    todo_list = TodoList.parse_message(todo_list_message.content)
    task_with_user = f"{task} ({interaction.user.name})"
    todo_list.add_todo_item(task_with_user)

    await todo_list_message.edit(content=str(todo_list))
    await interaction.response.send_message(f"Added task: {task_with_user}", ephemeral=True)
    

# @client.tree.command()
# async def done(interaction: discord.Interaction, item_number: int):
    

# @client.tree.command()
# async def undo(interaction: discord.Interaction, item_number: int):


# @client.tree.command()
# async def deleteDone(interaction: discord.Interaction, item_number: int):


# @client.tree.command()
# async def demo(interaction: discord.Interaction, link: str):
load_dotenv('.env')
discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)