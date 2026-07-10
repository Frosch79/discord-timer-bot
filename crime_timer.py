import asyncio
from datetime import timedelta
import discord

from utils import now_jst


async def normal_timer_loop(client):

    await client.wait_until_ready()

    while not client.is_closed():

        try:

            now = now_jst()

            for guild_id, timers in list(client.guild_timers.items()):

                remove = []

                # config取得（ここが分離対応ポイント）
                cfg = client.guild_config.get(guild_id, {})
                channel_id = cfg.get("channels", {}).get("crime")

                if not channel_id:
                    continue

                channel = client.get_channel(channel_id)
                if not channel:
                    continue

                role_id = cfg.get("role_id")

                mention = f"<@&{role_id}> " if role_id else ""

                for t in timers:

                    remaining = t["end"] - now

                    # 登録直後防止
                    if "last_remaining" not in t:
                        t["last_remaining"] = remaining
                        continue

                    last = t["last_remaining"]
                    t["last_remaining"] = remaining

                    def crossed(before, after, target):
                        return before > target and after <= target

                    checks = [
                        ("30", timedelta(minutes=30), "30分前"),
                        ("15", timedelta(minutes=15), "15分前"),
                        ("10", timedelta(minutes=10), "10分前"),
                        ("5", timedelta(minutes=5), "5分前"),
                    ]

                    for key, sec, text in checks:

                        if crossed(last, remaining, sec):

                            if key not in t["notified"]:

                                embed = discord.Embed(
                                    title="⚠ 犯罪タイマー通知",
                                    color=discord.Color.orange()
                                )

                                embed.add_field(
                                    name="🚨 犯罪",
                                    value=t["crime"],
                                    inline=False
                                )

                                embed.add_field(
                                    name="⌛ 残り",
                                    value=text,
                                    inline=True
                                )

                                unlock_time = t["end"].strftime("%H:%M")

                                embed.add_field(
                                    name="🕒 解禁時間",
                                    value=unlock_time,
                                    inline=True
                                )

                                await channel.send(
                                    content=mention,
                                    embed=embed
                                )

                                t["notified"].add(key)

                    # 解禁処理
                    if remaining <= timedelta(0):

                        if "end" not in t["notified"]:

                            embed = discord.Embed(
                                title="✅ 犯罪タイマー解禁",
                                color=discord.Color.green()
                            )

                            embed.add_field(
                                name="🚨 犯罪",
                                value=t["crime"],
                                inline=False
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

                            t["notified"].add("end")

                        remove.append(t)

                for t in remove:
                    if t in timers:
                        timers.remove(t)

        except Exception as e:
            print("crime_timer error:", e)

        await asyncio.sleep(10)
