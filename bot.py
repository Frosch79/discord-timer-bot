import discord
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import time
import os

# ===== TOKEN =====
#for local
load_dotenv()

#for deploy
TOKEN = os.getenv("TOKEN")


# ===== INTENTS =====
intents = discord.Intents.default()

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # ここは1回だけ実行される安全な場所
        await self.tree.sync()

    async def on_ready(self):
        print(f"ログイン完了: {self.user}")

client = MyClient()

# ===== クールダウン =====
COOLDOWNS = {
    "all": 10 * 60,
    "semi_heist": 30 * 60,
    "heist": 4 * 60 * 60
}

def can_use(user_last, user_id, category):
    now = time.time()

    if user_id not in user_last:
        return True, None

    last = user_last[user_id]

    # 全体クールダウン
    if now - last.get("all", 0) < COOLDOWNS["all"]:
        return False, COOLDOWNS["all"] - (now - last["all"])

    # 個別クールダウン
    if category in last:
        wait = COOLDOWNS.get(category, 0)
        if now - last[category] < wait:
            return False, wait - (now - last[category])

    return True, None

def set_use(user_last, user_id, category):
    now = time.time()

    if user_id not in user_last:
        user_last[user_id] = {}

    user_last[user_id]["all"] = now
    user_last[user_id][category] = now


# ===== TIMER =====
@client.tree.command(name="timer", description="分単位タイマー")
@app_commands.describe(minutes="分", message="終了メッセージ")
async def timer(interaction: discord.Interaction, minutes: int, message: str = "時間です！"):

    if minutes <= 0:
        await interaction.response.send_message("1分以上にしてください")
        return

    await interaction.response.send_message(f"{minutes}分タイマー開始")

    await asyncio.sleep(minutes * 60)

    await interaction.channel.send(
        f"{interaction.user.mention} ⏰ {message}"
    )


# ===== CRIME =====
@client.tree.command(name="crime", description="クールダウン付き犯罪コマンド")
@app_commands.describe(type="all / semi_heist / heist")
async def crime(interaction: discord.Interaction, type: str):

    if type not in COOLDOWNS:
        await interaction.response.send_message("❌ 無効なタイプです")
        return

    ok, wait = can_use(client.user_last, interaction.user.id, type)

    if not ok:
        await interaction.response.send_message(
            f"⛔ クールダウン中: あと {int(wait//60)}分"
        )
        return

    set_use(client.user_last, interaction.user.id, type)

    await interaction.response.send_message("✅ 犯罪成功（仮）")


# ===== RUN =====
print("ALL ENV KEYS:", list(os.environ.keys()))
print("TOKEN RAW:", os.getenv("TOKEN"))
client.run(TOKEN)
