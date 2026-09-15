from dataclasses import FrozenInstanceError
from random import Random
import unittest

from tournament import Entry, Tournament, count_votes, seed, seed_order


def tournament(size=21):
    return Tournament.create((str(i) for i in range(1, size + 1)), Random(0))


class TournamentTests(unittest.TestCase):
    def test_total_then_median_then_repeatable_random_ties(self):
        entries = [Entry("median", (7, 7, 1)), Entry("lower", (5, 5, 5)),
                   Entry("best", (10, 10, 10))]
        self.assertEqual(seed(entries, Random(0)), ("best", "median", "lower"))
        tied = [Entry(str(i), (5, 5, 5)) for i in range(10)]
        self.assertEqual(seed(tied, Random(9)), seed(tied, Random(9)))
        self.assertNotEqual(seed(tied, Random(9)), seed(tied, Random(10)))

    def test_invalid_entries_and_bracket_sizes(self):
        for scores in ((1, 2), (0, 2, 3), (11, 2, 3), (True, 2, 3), (1.5, 2, 3)):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                Entry("a", scores)
        for ids in ((), ("a",), ("a", "a"), ("a", ""), ("a", 2)):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                Tournament.create(ids)
        for size in (0, 1, 3, 12, -2, 2.0, True):
            with self.subTest(size=size), self.assertRaises(ValueError):
                seed_order(size)

    def test_standard_seed_positions(self):
        self.assertEqual(seed_order(8), (1, 8, 4, 5, 2, 7, 3, 6))

    def test_21_entries_have_five_wildcards_and_top_11_byes(self):
        jam = tournament()
        self.assertEqual(jam.stage, "Wildcard Preliminary")
        self.assertEqual(sum(not m.bye for m in jam.matches), 5)
        self.assertEqual({m.winner for m in jam.matches if m.bye}, {str(i) for i in range(1, 12)})
        pairs = {frozenset((m.a, m.b)) for m in jam.matches if not m.bye}
        self.assertEqual(pairs, {frozenset((str(i), str(33-i))) for i in range(12, 17)})

    def test_duplicates_double_reactions_and_exclusions(self):
        self.assertEqual(count_votes([1, 1, 2, 3, 8], [3, 4, 5, 9], [8, 9]), (2, 2))

    def test_majority_wins_and_ties_use_seed_not_A_B_order(self):
        for rng_seed in range(10):
            jam = Tournament.create(("best", "other"), Random(rng_seed)).open()
            for votes in ((0, 0), (18, 18)):
                self.assertEqual(jam.close([votes]).advance().champion, "best")
            self.assertEqual(jam.close([(1, 2)]).matches[0].winner, jam.matches[0].b)
            self.assertEqual(jam.close([(2, 1)]).matches[0].winner, jam.matches[0].a)

    def test_rounds_are_immutable_and_transitions_are_guarded(self):
        ready = tournament(2)
        voting = ready.open()
        closed = voting.close([(2, 1)])
        finished = closed.advance()
        self.assertEqual([j.phase for j in (ready, voting, closed, finished)],
                         ["ready", "voting", "closed", "finished"])
        self.assertIsNone(voting.matches[0].winner)
        with self.assertRaises(FrozenInstanceError):
            ready.phase = "finished"
        for action in (ready.advance, voting.advance, voting.open, closed.open,
                       lambda: closed.close([(1, 2)]), finished.advance):
            with self.assertRaises(ValueError):
                action()

    def test_failed_tally_does_not_partially_change_a_round(self):
        jam = tournament(4).open()
        for votes in ([], [(1, 2)], [(1, 2)]*3, [(1, 2), (-1, 2)],
                      [(1, 2), (True, 2)], [(1, 2), (1.5, 2)], [(1, 2), (1,)]):
            with self.subTest(votes=votes), self.assertRaises(ValueError):
                jam.close(votes)
            self.assertTrue(all(m.votes is None and m.winner is None for m in jam.matches))

    def test_full_tournaments_for_every_size_2_to_128(self):
        for size in range(2, 129):
            jam = tournament(size)
            total_matches = 0
            while jam.phase != "finished":
                active = [m for m in jam.matches if not m.bye]
                ids = [e for m in jam.matches for e in (m.a, m.b) if e is not None]
                self.assertEqual(len(ids), len(set(ids)))
                total_matches += len(active)
                closed = jam.open().close([(0, 0)] * len(active))
                winners = tuple(m.winner for m in closed.matches)
                jam = closed.advance(Random(0))
                if jam.phase != "finished":
                    for i, match in enumerate(jam.matches):
                        self.assertEqual({match.a, match.b}, set(winners[2*i:2*i+2]))
            self.assertEqual(jam.champion, "1")
            self.assertEqual(total_matches, size-1)


if __name__ == "__main__":
    unittest.main()
