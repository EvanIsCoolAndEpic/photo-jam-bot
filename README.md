# Photo Jam

A compact reference implementation for my Discord photo tournament. Made in python 3.10

## Try it

```sh
python demo.py
python -m unittest -v
```

only implemented currently for 16-round seeds.

- **Seeding:** sort by total judge score, then median. Shuffle before the stable sort to break exact ties. Preserve the resulting order throughout the tournament. O(n log n).
- **Bracket:** pad to the next power of two and recursively reflect seed positions. The highest seeds receive byes; a 21-entry field has five played prelims and 11 direct qualifiers. O(n).
- **Votes:** set subtraction removes duplicate identities, voters choosing both sides, and explicitly excluded voters. The Discord adapter also ignores bots. O(v).
- **Results:** the larger tally wins; equal tallies, including 0–0, advance the better seed.
- **State:** `ready → voting → closed → ready`, ending at `finished` after the final advancement. Each operation returns a new frozen state, so a rejected tally cannot partially change a round.
- **Invariant:** an n-entry single-elimination tournament plays exactly n−1 matches. Tests check every size from 2 through 128 and verify each winner follows the correct branch.

## Discord boundary

`discord_votes.tally(message)` reads a discord.py message's A/B reaction users and returns valid counts. It has no SDK import; the application that fetches the message supplies discord.py.
