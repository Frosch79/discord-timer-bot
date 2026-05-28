import discord
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import time
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # global sync
        await self.tree.sync()

    async def on_ready(self):
        print(f"ログイン完了: {self.user}")

        # guild sync
        for guild in self.guilds:
            try:
                await self.tree.sync(guild=guild)
                print(f"synced: {guild.name}")
            except Exception as e:
                print(f"sync failed: {guild.name} / {e}")

client = MyClient()

# =====================
# DATA
# =====================
guild_timers = {}
guild_config = {}  # ★重要

CRIMES = [
    "パレト",
    "輸送機",
    "ボブキャ",
    "ナイト",
    "軍事",
    "飛行場",
    "オイルリグ",
    "客船",
    "ヒューメイン",
    "アーティファクト",
    "ユニオン",
    "パシフィック"
]

# =====================
# ROLE SET
# =====================
@client.tree.command(name="set_crime_role")
@app_commands.describe(role="通知用ロール")
async def set_crime_role(interaction: discord.Interaction, role: discord.Role):

    guild_config[interaction.guild.id] = role.id

    await interaction.response.send_message(
        f"✅ 設定完了: {role.name}"
    )

# =====================
# TIMER SET
# =====================
@client.tree.command(name="crime_set", description="クールタイマー登録")
@app_commands.describe(
    crime="犯罪名",
    minutes="残り時間（分）"
)
@app_commands.choices(crime=[
    app_commands.Choice(name=c, value=c) for c in CRIMES
])
async def crime_set(interaction: discord.Interaction, crime: app_commands.Choice[str], minutes: int):

    guild_id = interaction.guild.id
    end_time = time.time() + minutes * 60

    if guild_id not in guild_timers:
        guild_timers[guild_id] = []

    guild_timers[guild_id].append({
        "crime": crime.value,
        "end": end_time,
        "notified": set(),
        "channel_id": interaction.channel.id,
        "created": time.time()
    })

    await interaction.response.send_message(
        f"🟢 {crime.value} 登録完了（{minutes}分）"
    )

# =====================
# STATUS
# =====================
@client.tree.command(name="crime_status")
async def crime_status(interaction: discord.Interaction):

    now = time.time()
    guild_id = interaction.guild.id

    if guild_id not in guild_timers:
        await interaction.response.send_message("データなし")
        return

    msg = "📊 クールタイム一覧\n\n"

    for t in guild_timers[guild_id]:
        remaining = t["end"] - now

        if remaining <= 0:
            continue
        else:
            msg += f"{t['crime']}: ⛔ {int(remaining//60)}分\n"

    await interaction.response.send_message(msg)

# =====================
# LOOP
# =====================
async def timer_loop():
    await client.wait_until_ready()

    while not client.is_closed():
        now = time.time()

        for guild_id, timers in list(guild_timers.items()):
            for t in timers:

                channel = client.get_channel(t["channel_id"])
                if not channel:
                    continue

                guild_id = channel.guild.id
                role_id = guild_config.get(guild_id)

                if not role_id:
                    continue

                remaining = t["end"] - now
                last = t.get("last_remaining")
                t["last_remaining"] = remaining

                if last is None:
                    continue

                def crossed(a, b, target):
                    return a > target and b <= target

                if crossed(last, remaining, 30*60) and "30" not in t["notified"]:
                    await channel.send(f"<@&{role_id}> ⚠ {t['crime']} 30分前")
                    t["notified"].add("30")

                if crossed(last, remaining, 15*60) and "15" not in t["notified"]:
                    await channel.send(f"<@&{role_id}> ⚠ {t['crime']} 15分前")
                    t["notified"].add("15")

                if crossed(last, remaining, 10*60) and "10" not in t["notified"]:
                    await channel.send(f"<@&{role_id}> ⚠ {t['crime']} 10分前")
                    t["notified"].add("10")

                if crossed(last, remaining, 5*60) and "5" not in t["notified"]:
                    await channel.send(f"<@&{role_id}> ⚠ {t['crime']} 5分前")
                    t["notified"].add("5")

                if remaining <= 0 and "end" not in t["notified"]:
                    await channel.send(f"<@&{role_id}> ✅ {t['crime']} 解禁！")
                    t["notified"].add("end")
                    timers.remove(t)

                    continue

        await asyncio.sleep(10)

@client.event
async def on_ready():
    client.loop.create_task(timer_loop())
    print(f"READY: {client.user}")

client.run(TOKEN)
