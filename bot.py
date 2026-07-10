from datetime import timedelta
import discord
from discord import app_commands
from config import TOKEN, CRIMES
from views import CoolView, CoolRemoveView
from crime_timer import normal_timer_loop
import asyncio
from cool_timer import cool_timer_loop
from utils import now_jst


intents = discord.Intents.default()


class MyClient(discord.Client):

    def __init__(self):

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

        self.guild_timers = {}
        self.guild_config = {}

    async def setup_hook(self):

        synced = await self.tree.sync()
        print(f"{len(synced)} commands synced")

        asyncio.create_task(normal_timer_loop(self))
        asyncio.create_task(cool_timer_loop(self))


client = MyClient()


@client.event
async def on_ready():
    print(f"READY {client.user}")


# -----------------
# プレイヤー登録
# -----------------

from players import add_player, remove_player, get_players


@client.tree.command(name="player_add", description="プレイヤー登録")
async def player_add(interaction: discord.Interaction, name: str):

    ok = add_player(interaction.guild.id, name)

    await interaction.response.send_message(
        f"登録: {name}" if ok else "すでに登録済み"
    )


@client.tree.command(name="player_list", description="登録プレイヤー一覧")
async def player_list(interaction: discord.Interaction):

    data = get_players(interaction.guild.id)

    if not data:
        await interaction.response.send_message("登録者なし")
        return

    embed = discord.Embed(
        title="👥 登録プレイヤー一覧",
        color=discord.Color.blue()
    )
    embed.description = "\n".join(data)

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="player_remove", description="プレイヤー削除")
async def player_remove(interaction: discord.Interaction, name: str):

    result = remove_player(interaction.guild.id, name)

    embed = discord.Embed(
        title="🗑 削除" if result else "⚠ 失敗",
        description=f"{name}" if result else "存在しません",
        color=discord.Color.red() if result else discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed)


# -----------------
# クール登録
# -----------------

from database import cooldowns


@client.tree.command(name="cool_add", description="犯罪クール登録")
async def cool_add(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🚨 犯罪クール登録",
        description="犯罪・参加者を選択してください。",
        color=discord.Color.green()
    )

    await interaction.response.send_message(
        embed=embed,
        view=CoolView(interaction.guild.id)
    )


# -----------------
# cool_status
# -----------------


@client.tree.command(
    name="cool_status",
    description="クールタイム一覧"
)
async def cool_status(interaction: discord.Interaction):

    data = cooldowns.get(interaction.guild.id, [])

    if not data:
        await interaction.response.send_message("現在クールなし")
        return

    now = now_jst()

    embed = discord.Embed(
        title="📊 クールタイム一覧",
        color=discord.Color.orange()
    )

    for c in data:

        value = ""

        value += (
            "👥 **参加者**\n"
            f"{', '.join(c['members'])}\n\n"
        )

        for rule, timer in c["cooldowns"].items():

            seconds = int((timer["end"] - now).total_seconds())

            if seconds <= 0:
                continue

            h = seconds // 3600
            m = (seconds % 3600) // 60

            remain = f"{h}時間 {m}分" if h else f"{m}分"

            end = timer["end"]

            value += (
                f"⏱ **{rule}**\n"
                f"⛔ 残り {remain}（{end.strftime('%H:%M')}）\n\n"
            )

        embed.add_field(
            name=f"🚨 {c['crime']}",
            value=value,
            inline=False
        )

        embed.add_field(
            name="\u200b",
            value="────────────",
            inline=False
        )

    embed.set_footer(text=f"登録件数：{len(data)}件")

    await interaction.response.send_message(embed=embed)

# -----------------
# クール削除
# -----------------

@client.tree.command(name="cool_remove", description="犯罪クール削除")
async def cool_remove(interaction: discord.Interaction):

    if not cooldowns.get(interaction.guild.id):
        await interaction.response.send_message("現在クールなし", ephemeral=True)
        return

    embed = discord.Embed(
        title="🗑 クール削除",
        description="削除する犯罪を選択してください。",
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=CoolRemoveView(interaction.guild.id),
        ephemeral=True
    )


# -----------------
# ロール設定（FIX済み）
# -----------------

@client.tree.command(name="set_crime_role", description="通知ロール設定")
async def set_crime_role(interaction: discord.Interaction, role: discord.Role):

    cfg = client.guild_config.setdefault(interaction.guild.id, {
        "role_id": None,
        "channels": {
            "crime": None,
            "cool": None
        }
    })

    cfg["role_id"] = role.id

    await interaction.response.send_message(
        f"🔔 設定完了: {role.mention}"
    )


# -----------------
# チャンネル設定（FIX済み）
# -----------------

@client.tree.command(name="set_crime_channel")
async def set_crime_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    cfg = client.guild_config.setdefault(interaction.guild.id, {
        "role_id": None,
        "channels": {
            "crime": None,
            "cool": None
        }
    })

    cfg["channels"]["crime"] = channel.id

    await interaction.response.send_message(f"crime → {channel.mention}")


@client.tree.command(name="set_cool_channel")
async def set_cool_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    cfg = client.guild_config.setdefault(interaction.guild.id, {
        "role_id": None,
        "channels": {
            "crime": None,
            "cool": None
        }
    })

    cfg["channels"]["cool"] = channel.id

    await interaction.response.send_message(f"cool → {channel.mention}")


# -----------------
# crime_set（FIX済み）
# -----------------

@client.tree.command(name="crime_set", description="犯罪登録")
@app_commands.choices(
    crime=[app_commands.Choice(name=x, value=x) for x in CRIMES]
)
async def crime_set(interaction: discord.Interaction,
                     crime: app_commands.Choice[str],
                     minutes: int):

    guild_id = interaction.guild.id

    if guild_id not in client.guild_timers:
        client.guild_timers[guild_id] = []

    client.guild_timers[guild_id] = [
        t for t in client.guild_timers[guild_id]
        if t["crime"] != crime.value
    ]

    end_time = now_jst() + timedelta(minutes=minutes)

    cfg = client.guild_config.get(guild_id, {})
    channel_id = cfg.get("channels", {}).get("crime")

    if not channel_id:
        await interaction.response.send_message("❌ crimeチャンネル未設定")
        return

    client.guild_timers[guild_id].append({
        "crime": crime.value,
        "end": end_time,
        "channel_id": channel_id,
        "notified": set()
    })

    unlock_time = end_time.strftime("%H:%M")

    embed = discord.Embed(
        title="🟢 犯罪タイマー登録",
        color=discord.Color.green()
    )

    embed.add_field(name="🚨 犯罪", value=crime.value)
    embed.add_field(name="⏱ 時間", value=f"{minutes}分")
    embed.add_field(name="🕒 解禁", value=unlock_time)

    await interaction.response.send_message(embed=embed)


# -----------------
# crime_status（FIX済み）
# -----------------

@client.tree.command(name="crime_status", description="登録中タイマー")
async def crime_status(interaction: discord.Interaction):

    guild_id = interaction.guild.id
    timers = client.guild_timers.get(guild_id, [])

    if not timers:
        await interaction.response.send_message("現在タイマーなし")
        return

    now = now_jst()

    embed = discord.Embed(
        title="📊 犯罪タイマー一覧",
        color=discord.Color.orange()
    )

    count = 0

    for t in timers:

        remaining = t["end"] - now

        if remaining <= timedelta(0):
            continue

        seconds = int(remaining.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        remain = f"{hours}時間 {minutes}分" if hours else f"{minutes}分"

        embed.add_field(
            name=f"🚨 {t['crime']}",
            value=f"⛔ 残り {remain}\n🕒 解禁 {t['end'].strftime('%H:%M')}",
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value="────────────",
            inline=False
        )

        count += 1

    if count == 0:
        embed.description = "現在タイマーなし"

    await interaction.response.send_message(embed=embed)


client.run(TOKEN)
