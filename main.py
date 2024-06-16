import nextcord
from nextcord.ext import commands
from javascript import require, On, off
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mineflayer = require('mineflayer')
mineflayerViewer = require('prismarine-viewer').mineflayer

token = '____'
guild_id = 0

bot = commands.Bot(help_command=None)

class Modal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("WTF????")
        self.host = nextcord.ui.TextInput(
            label="Enter host",
            min_length=1,
            max_length=100,
            required=True
        )
        self.port = nextcord.ui.TextInput(
            label="Enter port",
            min_length=1,
            max_length=5,
            required=True
        )
        self.username = nextcord.ui.TextInput(
            label="Enter username",
            min_length=1,
            max_length=16,
            required=True
        )
        self.version = nextcord.ui.TextInput(
            label="Enter mc version",
            min_length=1,
            max_length=8,
            required=True
        )

        self.add_item(self.host)
        self.add_item(self.port)
        self.add_item(self.username)
        self.add_item(self.version)
        
    async def callback(self, interaction: nextcord.Interaction):
        host = self.host.value
        port = int(self.port.value)
        username = self.username.value
        version = self.version.value

        logger.info(f"Trying to connect to {host}:{port} as {username} ({version})")

        try:
            botmc = mineflayer.createBot({
                'host': host,
                'port': port,
                'username': username,
                'version': version
            })
            mineflayerViewer(botmc, { port: 3000 , "firstPerson": True})
        except Exception as e:
            logger.error(f"Failed to create bot:")
            await interaction.response.send_message(content=f"Failed to create bot", ephemeral=True)
            return

        mes = await interaction.response.send_message(content=f'Connecting to {host}:{port} as {username} ({version})...', ephemeral=True)

        loop = asyncio.get_event_loop()

        @On(botmc, "login")
        def login(*args):
            bot_socket = botmc._client.socket
            logger.info(f"Logged in to {bot_socket.server if bot_socket.server else bot_socket._host}")
            embed = nextcord.Embed(title=f"Logged in to {bot_socket.server if bot_socket.server else bot_socket._host}")
            asyncio.run_coroutine_threadsafe(interaction.edit_original_message(embed=embed, content=None, view=myview), loop)

        @On(botmc, 'spawn')
        def spawn(*args):
            pos = botmc.entity.position
            logger.info(f"Spawned at x: {pos.x}, y: {pos.y}, z: {pos.z}")
            embed = nextcord.Embed(title=f"Spawned at x: {pos.x:.3f}, y: {pos.y:.3f}, z: {pos.z:.3f}")
            asyncio.run_coroutine_threadsafe(interaction.edit_original_message(embed=embed, content=None, view=myview), loop)

        @On(botmc, "death")
        def death(*args):
            logger.info("Bot died")
            embed = nextcord.Embed(title='Bot died')
            asyncio.run_coroutine_threadsafe(interaction.edit_original_message(embed=embed, content=None, view=myview), loop)

        @On(botmc, "kicked")
        def kicked(reason, *args):
            logger.info(f"Kicked from server")
            embed = nextcord.Embed(title=f"Kicked from server")
            asyncio.run_coroutine_threadsafe(interaction.edit_original_message(embed=embed, content=None, view=myview), loop)

        @On(botmc, "end")
        def end(reason, *args):
            logger.info(f"Disconnected")
            embed = nextcord.Embed(title=f"Disconnected")
            asyncio.run_coroutine_threadsafe(interaction.edit_original_message(embed=embed, content=None, view=None), loop)
            off(botmc, "login", login)
            off(botmc, "kicked", kicked)
            off(botmc, "end", end)
            off(botmc, "death", death)
            off(botmc, "spawn", spawn)

        async def button_callback(interaction: nextcord.Interaction):
            value = interaction.data['custom_id']
            botmcx = botmc.entity.yaw
            botmcy = botmc.entity.pitch
            if value == 'left':
                botmc.look(botmcx + 0.5, 0)
            if value == 'right':
                botmc.look(botmcx - 0.5, 0)
            if value == 'up':
                botmc.look(botmcx, botmcy + 0.5)
            if value == 'down':
                botmc.look(botmcx, botmcy - 0.5)
            if value == 'jump':
                botmc.setControlState('jump', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('jump', False) 
            if value == 'shift':
                botmc.setControlState('sneak', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('sneak', False)        
            if value == 'w':
                botmc.setControlState('forward', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('forward', False)      
            if value == 's':
                botmc.setControlState('back', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('back', False)
            if value == 'a':
                botmc.setControlState('left', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('left', False)
            if value == 'd':
                botmc.setControlState('right', True)
                await asyncio.sleep(0.5)
                botmc.setControlState('right', False)
            pos = botmc.entity.position
            embed = nextcord.Embed(title=f"current pos x: {pos.x:.3f}, y: {pos.y:.3f}, z: {pos.z:.3f}",description=f"look pos x: {botmc.entity.yaw:.3f}, y: {botmc.entity.pitch:.3f}")
            await mes.edit(embed=embed, content=None, view=myview)

        myview = nextcord.ui.View()
        buttons = [
            ('sneak', 'shift', 1), ('W', 'w', 1), ('jump', 'jump', 1),
            ('A', 'a', 2), ('S', 's', 2), ('D', 'd', 2),
            ('⬛', 'Not6', 3), ('⬆', 'up', 3), ('⬛', 'Not99', 3),
            ('⬅', 'left', 4), ('⬇', 'down', 4), ('➡', 'right', 4)
        ]
        for label, custom_id, row in buttons:
            button = nextcord.ui.Button(label=label, custom_id=custom_id, row=row)
            button.callback = button_callback
            myview.add_item(button)

class Button(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="What?", style=nextcord.ButtonStyle.green, custom_id="wtf")
    async def wtf(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(Modal())

@bot.event
async def on_ready():
    print(bot.user)
    bot.add_view(Button())

@bot.slash_command(description="setup", guild_ids=[guild_id])
async def setup(interaction: nextcord.Interaction):
    if interaction.user.guild_permissions.administrator:
        embed = nextcord.Embed(title="stupid bot", color=0x000000)
        await interaction.channel.send(embed=embed, view=Button())
    else:
        embed = nextcord.Embed(title="fuvk u bitch", color=0x000000)
        await interaction.send(embed=embed, ephemeral=True)

bot.run(token)
