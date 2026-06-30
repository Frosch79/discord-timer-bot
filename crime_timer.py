import asyncio
import time
import discord


async def normal_timer_loop(client):

    await client.wait_until_ready()

    while not client.is_closed():

        try:

            now = time.time()


            for guild_id, timers in list(
                client.guild_timers.items()
            ):

                remove = []


                for t in timers:


                    channel = client.get_channel(
                        t["channel_id"]
                    )

                    if not channel:
                        continue



                    role_id = client.guild_config.get(
                        guild_id
                    )


                    mention = ""

                    if role_id:
                        mention = f"<@&{role_id}> "



                    remaining = t["end"] - now



                    # 登録直後防止
                    if "last_remaining" not in t:

                        t["last_remaining"] = remaining
                        continue



                    last = t["last_remaining"]


                    t["last_remaining"] = remaining



                    def crossed(
                        before,
                        after,
                        target
                    ):

                        return (
                            before > target
                            and after <= target
                        )



                    checks = [

                        ("30", 30*60, "30分前"),

                        ("15", 15*60, "15分前"),

                        ("10", 10*60, "10分前"),

                        ("5", 5*60, "5分前"),

                    ]



                    for key, sec, text in checks:


                        if crossed(
                            last,
                            remaining,
                            sec
                        ):


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

                                await channel.send(
                                    content=mention,
                                    embed=embed
                                )


                                t["notified"].add(key)





                    # 解禁

                    if remaining <= 0:


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


                            t["notified"].add(
                                "end"
                            )



                        remove.append(t)





                for t in remove:

                    if t in timers:
                        timers.remove(t)




        except Exception as e:

            print(
                "crime_timer error:",
                e
            )



        await asyncio.sleep(10)
