from database import players


def add_player(guild_id: int, name: str):

    if guild_id not in players:
        players[guild_id] = []

    if name not in players[guild_id]:
        players[guild_id].append(name)
        return True

    return False



def remove_player(guild_id: int, name: str):

    if guild_id not in players:
        return False

    if name in players[guild_id]:
        players[guild_id].remove(name)
        return True

    return False



def get_players(guild_id: int):

    return players.get(
        guild_id,
        []
    )
