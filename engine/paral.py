
import numpy as np
import parse_game as p
import net as net_module
import pandas as pd
import helpers
import imp
from sys import getsizeof
import tensorflow as tf
tf.test.is_gpu_available()

import multiprocessing
pgn = open('data/test/many_games.pgn').read()

char_per_move = 31
num_moves_thousand = 200
num_bytes = num_moves_thousand * char_per_move * 1000
NUM_CORES = 2

loop_start = 10
loop_end = 500


def calc(i):
  filename = 'data/arrays/arrays%03d.npz' % i
  print('Starting %s' % i)
  char_start = num_bytes * i
  char_end = char_start + num_bytes
  if char_end <= len(pgn):
    x, y = p.pgn_file_to_array(pgn[char_start: char_end])
    np.savez_compressed(filename, x=x, y=y)
    print('Done with %s' % i)

if __name__ == '__main__':
  with multiprocessing.Pool(NUM_CORES) as pool:
    pool.map(calc, range(loop_start, loop_end))
