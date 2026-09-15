"""Seeded single elimination. Pure rules; no Discord, files, or database."""
from dataclasses import dataclass, replace
from random import Random, SystemRandom
from statistics import median
from typing import Iterable, Literal

Phase = Literal["ready", "voting", "closed", "finished"]


@dataclass(frozen=True)
class Entry:
    id: str
    scores: tuple[int, int, int]

    def __post_init__(self):
        object.__setattr__(self, "scores", tuple(self.scores))
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Entry IDs must be nonempty strings.")
        if len(self.scores) != 3 or any(type(s) is not int or not 1 <= s <= 10 for s in self.scores):
            raise ValueError("Each entry needs three integer scores from 1 to 10.")


def seed(entries: Iterable[Entry], rng: Random | None = None) -> tuple[str, ...]:
    """Rank by total, then median; shuffle first to break exact ties fairly."""
    entries = list(entries)
    _validate_ids(tuple(e.id for e in entries))
    (rng or SystemRandom()).shuffle(entries)
    entries.sort(key=lambda e: (sum(e.scores), median(e.scores)), reverse=True)
    return tuple(e.id for e in entries)


def seed_order(size: int) -> tuple[int, ...]:
    """Standard bracket positions: 1–8, 4–5, 2–7, 3–6 for eight slots."""
    if type(size) is not int or size < 2 or size & (size - 1):
        raise ValueError("Bracket size must be a power of two, at least 2.")
    order = [1, 2]
    while len(order) < size:
        complement = 2 * len(order) + 1
        order = [position for s in order for position in (s, complement - s)]
    return tuple(order)


def count_votes(a: Iterable[int], b: Iterable[int], excluded: Iterable[int] = ()) -> tuple[int, int]:
    """One vote per person. Remove excluded IDs and people choosing both sides."""
    a, b, excluded = set(a), set(b), set(excluded)
    return len(a - b - excluded), len(b - a - excluded)


@dataclass(frozen=True)
class Match:
    a: str
    b: str | None
    votes: tuple[int, int] | None = None
    winner: str | None = None

    @property
    def bye(self) -> bool:
        return self.b is None


@dataclass(frozen=True)
class Tournament:
    seeds: tuple[str, ...]
    rounds: tuple[tuple[Match, ...], ...]
    phase: Phase = "ready"

    @classmethod
    def create(cls, seeds: Iterable[str], rng: Random | None = None) -> "Tournament":
        """Accept IDs already ordered best seed first; assign byes to top seeds."""
        seeds = tuple(seeds)
        _validate_ids(seeds)
        size = 1 << (len(seeds) - 1).bit_length()
        slots = [seeds[s - 1] if s <= len(seeds) else None for s in seed_order(size)]
        return cls(seeds, (_matches(slots, rng),))

    @property
    def matches(self) -> tuple[Match, ...]:
        return self.rounds[-1]

    @property
    def stage(self) -> str:
        if len(self.rounds) == 1 and any(m.bye for m in self.matches):
            return "Wildcard Preliminary"
        size = 2 * len(self.matches)
        return {2: "Final", 4: "Semifinals", 8: "Quarterfinals"}.get(size, f"Round of {size}")

    @property
    def champion(self) -> str | None:
        return self.matches[0].winner if self.phase == "finished" else None

    def open(self) -> "Tournament":
        self._expect("ready")
        return replace(self, phase="voting")

    def close(self, votes: Iterable[tuple[int, int]]) -> "Tournament":
        """Freeze one tally per non-bye match, in match order. Higher seed wins ties."""
        self._expect("voting")
        votes = tuple(votes)
        if len(votes) != sum(not m.bye for m in self.matches):
            raise ValueError("Supply one tally for each non-bye match.")
        tallies = iter(votes)
        rank = {entry: index for index, entry in enumerate(self.seeds)}
        resolved = []
        for match in self.matches:
            if match.bye:
                resolved.append(match)
                continue
            counts = tuple(next(tallies))
            if len(counts) != 2 or any(type(n) is not int or n < 0 for n in counts):
                raise ValueError("Vote counts must be two nonnegative integers.")
            if counts[0] == counts[1]:
                winner = min((match.a, match.b), key=rank.__getitem__)
            else:
                winner = match.a if counts[0] > counts[1] else match.b
            resolved.append(replace(match, votes=counts, winner=winner))
        return replace(self, rounds=self.rounds[:-1] + (tuple(resolved),), phase="closed")

    def advance(self, rng: Random | None = None) -> "Tournament":
        self._expect("closed")
        winners = tuple(m.winner for m in self.matches)
        if None in winners:
            raise ValueError("Every match must have a winner before advancing.")
        if len(winners) == 1:
            return replace(self, phase="finished")
        return replace(self, rounds=self.rounds + (_matches(winners, rng),), phase="ready")

    def _expect(self, phase: Phase):
        if self.phase != phase:
            raise ValueError(f"Expected {phase}, got {self.phase}.")


def _validate_ids(ids: tuple[str, ...]):
    if len(ids) < 2 or any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Supply at least two nonempty entry IDs.")
    if len(set(ids)) != len(ids):
        raise ValueError("Entry IDs must be unique.")


def _matches(slots, rng: Random | None) -> tuple[Match, ...]:
    rng = rng or SystemRandom()
    matches = []
    for a, b in zip(slots[::2], slots[1::2]):
        if a is None:
            a, b = b, a
        if b is not None and rng.randrange(2):
            a, b = b, a
        matches.append(Match(a, b, winner=a if b is None else None))
    return tuple(matches)
