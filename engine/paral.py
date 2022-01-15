import datetime
import multiprocessing
import numpy as np

from engine import parse_game as p
from engine import net as net_module
from engine import helpers


print("Loading file")
pgn = open('data/lichess/lichess_db_standard_rated_2017-04.pgn').read()
#pgn = open('data/test/many_games.pgn').read()
print("Loading done")

char_per_move = 31
num_moves_thousand = 200
num_bytes = num_moves_thousand * char_per_move * 1000
NUM_CORES = 7

loop_start = 0
loop_end = 500

def calc(i):
  filename = 'data/arrays/arrays%03d' % i
  date = datetime.datetime.now()
  print('Starting %03d at %s' % (i, date))
  char_start = num_bytes * i
  char_end = char_start + num_bytes
  if char_end <= len(pgn):
    x, y = p.pgn_file_to_array(pgn[char_start: char_end])
    np.savez_compressed(filename, x=x, y=y)
    print('Done with %03d' % i)

if __name__ == '__main__':
  with multiprocessing.Pool(NUM_CORES) as pool:
    pool.map(calc, range(loop_start, loop_end))
