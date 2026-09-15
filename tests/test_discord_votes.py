from types import SimpleNamespace
import unittest

from discord_votes import A, B, tally


class Reaction:
    def __init__(self, emoji, voters):
        self.emoji, self.voters = emoji, voters

    async def users(self, limit=None):
        for user_id, is_bot in self.voters:
            yield SimpleNamespace(id=user_id, bot=is_bot)


class DiscordVoteTests(unittest.IsolatedAsyncioTestCase):
    async def test_counts_people_instead_of_raw_reaction_totals(self):
        message = SimpleNamespace(reactions=[
            Reaction(A, [(1, False), (2, False), (3, True), (4, False)]),
            Reaction(B, [(2, False), (3, True), (5, False), (6, False)]),
            Reaction("👍", [(7, False)]),
        ])
        self.assertEqual(await tally(message, excluded=[6]), (2, 1))

    async def test_no_votes(self):
        self.assertEqual(await tally(SimpleNamespace(reactions=[])), (0, 0))

    async def test_failed_read_propagates_instead_of_returning_a_partial_tally(self):
        class UnavailableReaction:
            emoji = B

            async def users(self, limit=None):
                raise ConnectionError("Discord unavailable")
                yield

        message = SimpleNamespace(reactions=[Reaction(A, [(1, False)]), UnavailableReaction()])
        with self.assertRaises(ConnectionError):
            await tally(message)


if __name__ == "__main__":
    unittest.main()
