import discord
from discord import app_commands
import asyncio
import time
import os



class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.tree.sync()
        print(f"ログイン完了: {self.user}")

client = MyClient()


user_last = {}

COOLDOWNS = {
    "all": 10 * 60,
    "semi_heist": 30 * 60,
    "heist": 4 * 60 * 60
}

def can_use(user_id, category):
    now = time.time()

    if user_id not in user_last:
        return True, None

    last = user_last[user_id]

    # 全体クールダウン
    if now - last.get("all", 0) < COOLDOWNS["all"]:
        return False, COOLDOWNS["all"] - (now - last["all"])

    # 犯罪タイプ別
    if category in last:
        wait = COOLDOWNS.get(category, 0)
        if now - last[category] < wait:
            return False, wait - (now - last[category])

    return True, None


def set_use(user_id, category):
    now = time.time()

    if user_id not in user_last:
        user_last[user_id] = {}

    user_last[user_id]["all"] = now
    user_last[user_id][category] = now



#/timer
@client.tree.command(name="timer", description="分単位のタイマーをセットします")
@app_commands.describe(minutes="分", message="終了メッセージ")
async def timer(interaction: discord.Interaction, minutes: int, message: str = "時間です！"):

    if minutes <= 0:
        await interaction.response.send_message("1分以上にしてください")
        return

    seconds = minutes * 60

    await interaction.response.send_message(f"{minutes}分タイマー開始")

    await asyncio.sleep(seconds)

    await interaction.channel.send(f"{interaction.user.mention} ⏰ {message}")


#/crime
@client.tree.command(name="crime")
@app_commands.describe(type="all / semi_heist / heist")
async def crime(interaction: discord.Interaction, type: str):

    if type not in COOLDOWNS:
        await interaction.response.send_message("❌ 無効なタイプです")
        return

    ok, wait = can_use(interaction.user.id, type)

    if not ok:
        await interaction.response.send_message(
            f"⛔ クールダウン中: あと {int(wait//60)}分"
        )
        return

    set_use(interaction.user.id, type)

    await interaction.response.send_message("✅ 犯罪成功（仮）")

client.run(os.getenv("TOKEN"))
