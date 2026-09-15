"""The Discord boundary: turn reaction users into a pair of valid vote counts."""
from tournament import count_votes

A, B = "🅰️", "🅱️"


async def tally(message, excluded=()) -> tuple[int, int]:
    """Read a discord.py Message; exclude bots and users reacting to both choices."""
    voters = {A: set(), B: set()}
    for reaction in message.reactions:
        choice = str(reaction.emoji)
        if choice in voters:
            async for user in reaction.users(limit=None):
                if not user.bot:
                    voters[choice].add(user.id)
    return count_votes(voters[A], voters[B], excluded)
