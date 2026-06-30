import discord
from discord.ui import View, Select, Modal, TextInput
from config import CRIMES
from players import get_players
from utils import parse_time
from database import cooldowns
from datetime import  timedelta

SUCCESS_COLOR = discord.Color.green()
ERROR_COLOR = discord.Color.red()
WARNING_COLOR = discord.Color.orange()




class CrimeSelect(Select):

    def __init__(self, view):

        self.parent_view = view

        options=[
            discord.SelectOption(
                label=c
            )
            for c in CRIMES
        ]

        super().__init__(
            placeholder="犯罪を選択",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction):

        self.parent_view.crime=self.values[0]

        await interaction.response.defer()



class PlayerSelect(Select):

    def __init__(self, view, title):

        self.parent_view=view

        players=get_players(
            view.guild_id
        )


        options=[
            discord.SelectOption(
                label=p
            )
            for p in players
        ]


        super().__init__(
            placeholder=title,
            options=options,
            min_values=0,
            max_values=max(
                1,
                len(options)
            )
        )


    async def callback(self, interaction):

        self.parent_view.selected[
            self.placeholder
        ]=self.values


        await interaction.response.defer()



class CooldownModal(Modal):

    def __init__(self, view):

        self.parent_view=view

        super().__init__(
            title="シーン情報"
        )


        self.scene_end=TextInput(
            label="シーン終了時間 HH:MM",
            placeholder="21:10"
        )


        self.add_item(
            self.scene_end
        )



    async def on_submit(self, interaction):

        scene=parse_time(
            self.scene_end.value
        )

        guild=interaction.guild.id


        if guild not in cooldowns:
            cooldowns[guild]=[]



        cooldowns[guild].append({

            "crime":
            self.parent_view.crime,

            "scene":
            scene,

            "members":
            self.parent_view.selected.get(
                "参加者",
                []
            ),

            "arrest":
            self.parent_view.selected.get(
                "逮捕者",
                []
            ),

            "escape":
            self.parent_view.selected.get(
                "逃走者",
                []
            ),

            "profit":
            self.parent_view.profit,


            "cooldowns":{

                "4時間":{
                    "end":
                    scene + timedelta(hours=4),

                    "notify":[]
                },


                "30分":{
                    "end":
                    scene + timedelta(minutes=30),

                    "notify":[]
                }

            },


            "channel":
            interaction.channel.id

        })




        four = scene + timedelta(hours=4)
        thirty = scene + timedelta(minutes=30)



        embed = discord.Embed(
            title="🚨 犯罪登録",
            color=SUCCESS_COLOR
        )


        embed.add_field(
            name="🚨 犯罪",
            value=self.parent_view.crime,
            inline=False
        )


        embed.add_field(
            name="👥 参加者",
            value=", ".join(
                self.parent_view.selected.get(
                    "参加者",
                    []
                )
            ) or "なし",
            inline=False
        )


        embed.add_field(
            name="🚓 逮捕者",
            value=", ".join(
                self.parent_view.selected.get(
                    "逮捕者",
                    []
                )
            ) or "なし",
            inline=True
        )


        embed.add_field(
            name="🏃 逃走者",
            value=", ".join(
                self.parent_view.selected.get(
                    "逃走者",
                    []
                )
            ) or "なし",
            inline=True
        )


        embed.add_field(
            name="💰 利確",
            value=self.parent_view.profit,
            inline=True
        )


        embed.add_field(
            name="⏱ 4時間",
            value=f"""
        5分前:
        {(four-timedelta(minutes=5)).strftime("%H:%M")}

        解禁:
        {four.strftime("%H:%M")}
        """,
            inline=True
        )


        embed.add_field(
            name="⏱ 30分",
            value=f"""
        5分前:
        {(thirty-timedelta(minutes=5)).strftime("%H:%M")}

        解禁:
        {thirty.strftime("%H:%M")}
        """,
            inline=True
        )


        await interaction.response.send_message(
            embed=embed
        )



class CoolView(View):

    def __init__(self, guild_id):

        super().__init__(
            timeout=300
        )

        self.guild_id=guild_id

        self.crime=None

        self.selected={}

        self.profit="未設定"


        self.add_item(
            CrimeSelect(self)
        )

        self.add_item(
            PlayerSelect(
                self,
                "参加者"
            )
        )

        self.add_item(
            PlayerSelect(
                self,
                "逮捕者"
            )
        )

        self.add_item(
            PlayerSelect(
                self,
                "逃走者"
            )
        )


    @discord.ui.button(
        label="利確/成功",
        style=discord.ButtonStyle.green
    )
    async def profit_yes(
        self,
        interaction,
        button
    ):

        self.profit="成功"

        await interaction.response.defer()



    @discord.ui.button(
        label="利確/失敗",
        style=discord.ButtonStyle.red
    )
    async def profit_no(
        self,
        interaction,
        button
    ):

        self.profit="失敗"

        await interaction.response.defer()



    @discord.ui.button(
        label="登録",
        style=discord.ButtonStyle.blurple
    )
    async def register(
        self,
        interaction,
        button
    ):

        if not self.crime:

            await interaction.response.send_message(
                "犯罪を選択してください",
                ephemeral=True
            )
            return


        await interaction.response.send_modal(
            CooldownModal(self)
        )



class CoolRemoveSelect(Select):

    def __init__(self, guild_id):

        self.guild_id = guild_id

        options=[]

        for i, c in enumerate(
            cooldowns.get(guild_id, [])
        ):

            scene = c["scene"].strftime("%H:%M")

            options.append(
                discord.SelectOption(
                    label=c["crime"],
                    value=str(i),
                    description=f"{scene} | {', '.join(c['members'])}"
                )
            )


        super().__init__(
            placeholder="削除する犯罪",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction):

        index = int(
            self.values[0]
        )


        data = cooldowns.get(
            self.guild_id,
            []
        )


        c = data[index]

        scene = c["scene"].strftime("%H:%M")
        embed = discord.Embed(
            title="⚠ クール削除確認",
            color=ERROR_COLOR
        )


        embed.add_field(
            name="🚨 犯罪",
            value=c["crime"],
            inline=False
        )


        embed.add_field(
            name="⏰ シーン終了時間",
            value=scene,
            inline=True
        )


        embed.add_field(
            name="👥 参加者",
            value=", ".join(c["members"]),
            inline=False
        )


        await interaction.response.edit_message(
            embed=embed,
            view=ConfirmRemoveView(
                self.guild_id,
                index
            )
        )

class ConfirmRemoveView(View):

    def __init__(self, guild_id, index):

        super().__init__(
            timeout=60
        )

        self.guild_id = guild_id
        self.index = index


    @discord.ui.button(
        label="✅ 削除する",
        style=discord.ButtonStyle.red
    )
    async def confirm(
        self,
        interaction,
        button
    ):

        data = cooldowns.get(
            self.guild_id,
            []
        )


        if self.index >= len(data):

            await interaction.response.edit_message(
                content="すでに削除されています。",
                view=None
            )

            return



        removed = data.pop(
            self.index
        )


        embed = discord.Embed(
            title="🗑 削除しました",
            color=SUCCESS_COLOR
        )


        embed.add_field(
            name="🚨 犯罪",
            value=removed["crime"],
            inline=False
        )


        embed.add_field(
            name="👥 参加者",
            value=", ".join(
                removed["members"]
            ),
            inline=False
        )


        await interaction.response.edit_message(
            embed=embed,
            view=None
        )



    @discord.ui.button(
        label="❌ キャンセル",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="❌ キャンセル",
            description="削除をキャンセルしました。",
            color=ERROR_COLOR
        )


        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

class CoolRemoveView(View):

    def __init__(self, guild_id):

        super().__init__(
            timeout=60
        )

        self.add_item(
            CoolRemoveSelect(guild_id)
        )
