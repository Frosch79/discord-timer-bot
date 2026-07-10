import asyncio
from datetime import timedelta
import discord

from database import cooldowns
from utils import now_jst


async def cool_timer_loop(client):

    await client.wait_until_ready()

    while not client.is_closed():

        try:
            now = now_jst()

            for guild_id, items in list(cooldowns.items()):

                cfg = client.guild_config.get(guild_id, {})
                channel_id = cfg.get("channels", {}).get("cool")

                if not channel_id:
                    continue

                channel = client.get_channel(channel_id)

                if not channel:
                    continue

                role_id = cfg.get("role_id")
                mention = f"<@&{role_id}> " if role_id else ""

                remove = []

                for c in items:

                    for rule, timer in c["cooldowns"].items():

                        # =====================
                        # 時間計算
                        # =====================
                        remain = timer["end"] - now

                        last = timer.get("last_remaining", remain)
                        timer["last_remaining"] = remain

                        def crossed(before, after, target):
                            return before > target and after <= target

                        if not isinstance(timer.get("notify"), set):
                            timer["notify"] = set()

                        # =====================
                        # 事前通知
                        # =====================
                        checks = [
                            ("15", timedelta(minutes=15), "15分前"),
                            ("5", timedelta(minutes=5), "5分前"),
                        ]

                        for key, target, text in checks:

                            if crossed(last, remain, target):

                                if key not in timer["notify"]:

                                    embed = discord.Embed(
                                        title="⚠ 犯罪クールタイム通知",
                                        color=discord.Color.orange()
                                    )

                                    embed.add_field(
                                        name="🚨 犯罪",
                                        value=c["crime"],
                                        inline=False
                                    )

                                    embed.add_field(
                                        name="👥 参加者",
                                        value=", ".join(c["members"]),
                                        inline=False
                                    )

                                    embed.add_field(
                                        name="⏱ クール",
                                        value=rule,
                                        inline=True
                                    )

                                    embed.add_field(
                                        name="⌛ 残り",
                                        value=text,
                                        inline=True
                                    )

                                    await channel.send(
                                        content=mention,
                                        embed=embed
                                    )

                                    timer["notify"].add(key)

                        # =====================
                        # 解禁通知
                        # =====================
                        if remain <= timedelta(0):

                            if "end" not in timer["notify"]:

                                embed = discord.Embed(
                                    title="✅ 犯罪クール解禁",
                                    color=discord.Color.green()
                                )

                                embed.add_field(
                                    name="🚨 犯罪",
                                    value=c["crime"],
                                    inline=False
                                )

                                embed.add_field(
                                    name="👥 参加者",
                                    value=", ".join(c["members"]),
                                    inline=False
                                )

                                embed.add_field(
                                    name="⏱ クール",
                                    value=rule,
                                    inline=True
                                )

                                embed.add_field(
                                    name="状態",
                                    value="🟢 使用可能",
                                    inline=True
                                )

                                await channel.send(
                                    content=mention,
                                    embed=embed
                                )

                                timer["notify"].add("end")

                    # =====================
                    # 削除判定
                    # =====================
                    if all(
                        x["end"] <= now
                        for x in c["cooldowns"].values()
                    ):
                        remove.append(c)

                for c in remove:
                    items.remove(c)

        except Exception as e:
            print("cool_timer error:", e)

        await asyncio.sleep(10)
