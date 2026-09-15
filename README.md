# Photo Jam

A compact reference implementation of the algorithms behind a Discord photo tournament. Python 3.10+, standard library only.

Three judges seed the photos. A wildcard round fills a power-of-two bracket, then community votes eliminate one photo per match until a champion remains.

## Try it

```sh
python demo.py
python -m unittest -v
```

The deterministic demo runs 21 synthetic entries through five wildcard matches, a round of 16, quarterfinals, semifinals, and the final.

## Core API

```python
from tournament import Entry, Tournament, seed

entries = [Entry("forest", (8, 9, 7)), Entry("street", (7, 8, 6))]
jam = Tournament.create(seed(entries))
jam = jam.open()
jam = jam.close([(18, 18)])  # One (A, B) tally per non-bye match, in order.
jam = jam.advance()
print(jam.champion)         # forest: higher seed breaks the tie.
```

Already have seeds? Pass entry IDs to `Tournament.create()` in ranked order. A supplied `random.Random` makes seeding and A/B placement reproducible.

## The logic

- **Seeding:** sort by total judge score, then median. Shuffle before the stable sort to break exact ties. Preserve the resulting order throughout the tournament. O(n log n).
- **Bracket:** pad to the next power of two and recursively reflect seed positions. The highest seeds receive byes; a 21-entry field has five played prelims and 11 direct qualifiers. O(n).
- **Votes:** set subtraction removes duplicate identities, voters choosing both sides, and explicitly excluded voters. The Discord adapter also ignores bots. O(v).
- **Results:** the larger tally wins; equal tallies, including 0–0, advance the better seed.
- **State:** `ready → voting → closed → ready`, ending at `finished` after the final advancement. Each operation returns a new frozen state, so a rejected tally cannot partially change a round.
- **Invariant:** an n-entry single-elimination tournament plays exactly n−1 matches. Tests check every size from 2 through 128 and verify each winner follows the correct branch.

## Discord boundary

`discord_votes.tally(message)` reads a discord.py message's A/B reaction users and returns valid counts. It has no SDK import; the application that fetches the message supplies discord.py.

```python
from discord_votes import tally

# Inside your application's async close-round handler:
counts = [await tally(message) for message in ballot_messages]
jam = jam.close(counts)
```

Supply messages in non-bye match order. Everyone may vote by default; pass excluded user IDs when needed. A failed Discord read raises instead of silently awarding a match.

This repository is the logic extracted for study and reuse. The live bot's commands, authentication, persistence, retry handling, photo storage, and bracket artwork remain in the event application. Integration must serialize organizer actions, enforce a voting cutoff, and persist accepted states; reaction reads are not an atomic snapshot across Discord messages.
