
# Testing
`nosetests -v test_parse_game.py 2>&1 | grep -v "tensorflow" | grep -v "np_"`

# Generating the data:
## Download
```
mkdir -p data/lichess
wget https://database.lichess.org/standard/lichess_db_standard_rated_2017-04.pgn.bz2
bzip2 -d lichess_db_standard_rated_2017-04.pgn.bz2

cat ~/Downloads/lichess_db_standard_rated_2017-04.pgn | head -1000000 | grep -v "\[Site" > data/test/many_games.pgn
```

## Splitting into chunks
`cd ~/human_chess_engine; PYTHONPATH=. python3 -m engine.paral`

# Speed:

8/17/8pm: 26K moves parsed / minuted
8/24/4pm: 45K moves parsed / minute

- Can I reduce memory usage through sparse array?
- What is best approach to use large amout of data?
- How can I stop training, load new data, then keep training


# Todo:

- Checks: Time is scaled into 0-1 format
