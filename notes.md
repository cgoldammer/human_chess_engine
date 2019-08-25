
# Generating the data:
`cat ~/Downloads/lichess_db_standard_rated_2017-04.pgn | head -1000000 | grep -v "\[Site" > data/test/many_games.pgn`
`nosetests -v test_parse_game.py 2>&1 | grep -v "tensorflow" | grep -v "np_"`

# Speed:

8/17/8pm: 26K moves parsed / minuted
8/24/4pm: 45K moves parsed / minute


# Todo:

- Checks: 
  - Am I inverting correctly if it's black to move?
    - Fen
    - Ratings
    - EP
- Scale time into 0-1 format
- Include total game time
- Include rating and opponent rating

