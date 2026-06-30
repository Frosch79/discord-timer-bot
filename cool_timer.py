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

                remove=[]


                for c in items:


                    channel = client.get_channel(
                        c["channel"]
                    )


                    if not channel:
                        continue



                    for rule, timer in c["cooldowns"].items():


                        remain = timer["end"] - now


                        last = timer.get(
                            "last_remaining"
                        )


                        timer["last_remaining"] = remain



                        # 登録直後は記録だけ
                        if last is None:
                            continue



                        def crossed(
                            before,
                            after,
                            target
                        ):

                            return (
                                before > target
                                and after <= target
                            )



                        role_id = client.guild_config.get(
                            guild_id
                        )


                        mention=""

                        if role_id:
                            mention=f"<@&{role_id}> "




                        checks = [
                            ("15", timedelta(minutes=15), "15分前"),
                            ("5", timedelta(minutes=5), "5分前"),
                        ]


                        for key, target, text in checks:


                            if crossed(
                                last,
                                remain,
                                target
                            ):


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


                                    timer["notify"].append(key)



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

                                timer["notify"].append("end")



                    # 4時間も30分も終わったら削除
                    if all(
                        "end" in x["notify"]
                        for x in c["cooldowns"].values()
                    ):

                        remove.append(c)



                for c in remove:

                    items.remove(c)



        except Exception as e:

            print(
                "cool_timer error:",
                e
            )


        await asyncio.sleep(10)
