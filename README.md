# Photo Jam

My Discord photo tournament project. Right now I'm working on the rules: how photos get seeded, who plays who, and what actually counts as a vote. Python 3.10+.

## Where I'm at

The tournament logic is here, along with a small adapter for reading Discord reactions. The test currently runs a 21-photo tournament with made-up scores and votes for flagging.

I want the bracket to be predictable enough that I can explain why someone advanced. Getting that right matters more to me at this stage than adding commands around it.

## Rules I'm going with

- Three judge scores per photo, each from 1–10. Total score decides seeding, then median. Exact ties get shuffled (TODO: make fix).
- Better seeds get the byes. With 21 photos (as an example), that means five preliminary matches and 11 photos going straight through.
- Once the bracket is set, it stays set. Winners follow their branch; A/B placement can change without changing who they face.
- One vote per person. React to both photos and neither vote counts. Bots and explicitly excluded voters don't count either.
- A tied match goes to the better seed, including 0–0. That's the tiebreak I'm using for now.
- A bad tally should fail the whole update. I don't think this would happen but it'll just stop it so i can input the scores myself. wallahi that never happens.

## Run it

```sh
python demo.py
python -m unittest -v
```

Run these from the repo root. The demo and tests use the standard library.

## What I've checked

The tests live in `tests/`. They cover seeding, byes, duplicate votes, ties, invalid tallies, and attempts to advance a round before it's ready. They also run complete tournaments for every entry count from 2 through 128, checking that winners stay on the right branch and that each tournament plays exactly one fewer match than it has entries.

That checks the rules locally. Running the whole thing in Discord is still work to do. `discord_votes.py` can tally A/B reaction users from a supplied message, but something still needs to connect to Discord and fetch that message.

if you have better implementation send me a pull request.
