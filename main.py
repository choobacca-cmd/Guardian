import discord
from discord.ext import commands
from discord import app_commands
from discord import Color, Embed, ButtonStyle
from discord.ui import Button, View
import os
from dotenv import load_dotenv
load_dotenv()

VOICE_CHANNEL_ROLES = {
    1396079559702614016: 1396078977969553519,  # Канал 1 → Роль 1
    1396079947746902076: 1396079049155018793,  # Канал 2 → Роль 2
    1396080026750943243: 1396079102468821024,  # Канал 3 → Роль 3
    1396080086926622841: 1396079143493304370,  # Канал 4 → Роль 4
    1396081322698604584: 1396079204608507945,  # Канал 5 → Роль 5
    1396081423190069298: 1396079234568425584,  # Канал 6 → Роль 6
    1396081504316035103: 1396079262846554122,  # Канал 7 → Роль 7
    1396081549438353498: 1396079304386809970   # Канал 8 → Роль 8
}

default_role_id = 1396072475053265008 

GUILD_ID = 1396069780766724186

intents = discord.Intents.all()
intents.members = True  # Необхідно для відстеження учасників
intents.voice_states = True  # Необхідно для відстеження голосових каналів

bot = commands.Bot(command_prefix='!', intents=intents)

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("❌ Ця команда доступна лише адміністраторам!", ephemeral=True)
        return False
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} готовий!')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Синхронізовано {len(synced)} команд")
    except Exception as e:
        print(f"Помилка синхронізації: {e}")

class LanguageView(View):
    def __init__(self, original_embed, russian_text, english_text):
        super().__init__(timeout=None)
        self.original_embed = original_embed
        self.russian_text = russian_text
        self.english_text = english_text
        
    @discord.ui.button(label="Русский", style=ButtonStyle.gray, emoji="🇷🇺")
    async def russian_button(self, interaction: discord.Interaction, button: Button):
        for field in self.russian_text['fields']:
            self.original_embed.add_field(name=field['name'], value=field['value'], inline=field.get('inline', False))
        
        if 'image' in self.russian_text:
            self.original_embed.set_image(url=self.russian_text['image'])
        if 'thumbnail' in self.russian_text:
            self.original_embed.set_thumbnail(url=self.russian_text['thumbnail'])
            
        self.original_embed.description = self.russian_text['description']
        await interaction.response.edit_message(embed=self.original_embed)
        
    @discord.ui.button(label="English", style=ButtonStyle.gray, emoji="🇬🇧")
    async def english_button(self, interaction: discord.Interaction, button: Button):
        for field in self.english_text['fields']:
            self.original_embed.add_field(name=field['name'], value=field['value'], inline=field.get('inline', False))
        
        if 'image' in self.english_text:
            self.original_embed.set_image(url=self.english_text['image'])
        if 'thumbnail' in self.english_text:
            self.original_embed.set_thumbnail(url=self.english_text['thumbnail'])
            
        self.original_embed.description = self.english_text['description']
        await interaction.response.edit_message(embed=self.original_embed)

@bot.tree.command(name="embed", description="Create a beautiful custom embed with language options", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    title="Embed title",
    description="Embed description",
    color="Embed color in HEX (e.g. #3498db)",
    url="URL for the title (optional)",
    author_name="Author name (optional)",
    author_icon="Author icon URL (optional)",
    footer_text="Footer text (optional)",
    footer_icon="Footer icon URL (optional)",
    image_url="Image URL (optional)",
    thumbnail_url="Thumbnail URL (optional)",
    russian_description="Russian version of description (optional)",
    english_description="English version of description (optional)"
)
@is_admin()
async def embed(
    interaction: discord.Interaction,
    title: str,
    description: str,
    color: str = "#3498db",
    url: str = None,
    author_name: str = None,
    author_icon: str = None,
    footer_text: str = None,
    footer_icon: str = None,
    image_url: str = None,
    thumbnail_url: str = None,
    russian_description: str = None,
    english_description: str = None
):
    # Convert color
    try:
        if color.startswith("#"):
            color = color.lstrip("#")
        color_int = int(color, 16)
        embed_color = Color(color_int)
    except Exception:
        embed_color = Color.blue()

    embed = Embed(title=title, description=description, color=embed_color, url=url)

    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon)

    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon)

    if image_url:
        embed.set_image(url=image_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    embed.timestamp = discord.utils.utcnow()

    # Prepare language options if provided
    if russian_description or english_description:
        # Default texts (use main description if language-specific not provided)
        russian_text = {
            'description': russian_description if russian_description else description,
            'fields': [],
            'image': image_url,
            'thumbnail': thumbnail_url
        }
        
        english_text = {
            'description': english_description if english_description else description,
            'fields': [],
            'image': image_url,
            'thumbnail': thumbnail_url
        }
        
        view = LanguageView(embed, russian_text, english_text)
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed)
# Команда очищення чату (тільки для адмінів)
@bot.tree.command(name="clear", description="Очистити чат", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(amount="Кількість повідомлень для видалення")
@is_admin()
async def clear(interaction: discord.Interaction, amount: int = 10):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Видалено {amount} повідомлень!", ephemeral=True)

# Команда бану (тільки для адмінів)
@bot.tree.command(name="ban", description="Забанити користувача", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Користувач для бану", reason="Причина бану")
@is_admin()
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Не вказано"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Користувача {user.mention} забанено! Причина: {reason}")

# Команда кіку (тільки для адмінів)
@bot.tree.command(name="kick", description="Кікнути користувача", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Користувач для кіку", reason="Причина кіку")
@is_admin()
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Не вказано"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 Користувача {user.mention} кікнуто! Причина: {reason}")

# Команда муту (тільки для адмінів)
@bot.tree.command(name="mute", description="Замутити користувача", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Користувач для муту", reason="Причина муту")
@is_admin()
async def mute(interaction: discord.Interaction, user: discord.Member, reason: str = "Не вказано"):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)
    
    await user.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"🔇 Користувача {user.mention} замучено! Причина: {reason}")

# Команда розмуту (тільки для адмінів)
@bot.tree.command(name="unmute", description="Розмутити користувача", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Користувач для розмуту")
@is_admin()
async def unmute(interaction: discord.Interaction, user: discord.Member):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if muted_role and muted_role in user.roles:
        await user.remove_roles(muted_role)
        await interaction.response.send_message(f"🔊 Користувача {user.mention} розмучено!")
    else:
        await interaction.response.send_message("❌ Цей користувач не замучений!", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    # Якщо користувач зайшов у канал → видати відповідну роль
    if after.channel and after.channel.id in VOICE_CHANNEL_ROLES:
        role_id = VOICE_CHANNEL_ROLES[after.channel.id]
        role = member.guild.get_role(role_id)
        
        if role and role not in member.roles:
            try:
                await member.add_roles(role)
                print(f'✅ {member.name} отримав роль {role.name} (зайшов у {after.channel.name})')
            except Exception as e:
                print(f'❌ Помилка видачі ролі: {e}')

    # Якщо користувач вийшов з каналу → забрати відповідну роль
    if before.channel and before.channel.id in VOICE_CHANNEL_ROLES:
        role_id = VOICE_CHANNEL_ROLES[before.channel.id]
        role = member.guild.get_role(role_id)
        
        if role and role in member.roles:
            try:
                await member.remove_roles(role)
                print(f'❌ {member.name} втратив роль {role.name} (вийшов з {before.channel.name})')
            except Exception as e:
                print(f'⚠️ Помилка видалення ролі: {e}')

# Запуск бота
bot.run(os.getenv("TOKEN"))