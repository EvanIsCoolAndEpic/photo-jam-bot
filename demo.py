"""A repeatable 21-photo tournament with synthetic scores and votes."""
from random import Random
from tournament import Entry, Tournament, seed


def main():
    rng = Random(7)
    entries = [Entry(f"photo-{i:02d}", tuple(rng.randint(1, 10) for _ in range(3)))
               for i in range(1, 22)]
    jam = Tournament.create(seed(entries, rng), rng)
    while jam.phase != "finished":
        playing = [m for m in jam.matches if not m.bye]
        byes = sum(m.bye for m in jam.matches)
        print(f"{jam.stage}: {len(playing)} matches, {byes} byes")
        votes = [(rng.randrange(20), rng.randrange(20)) for _ in playing]
        jam = jam.open().close(votes).advance(rng)
    print(f"Champion: {jam.champion}")


if __name__ == "__main__":
    main()
