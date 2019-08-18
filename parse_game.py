from collections import namedtuple
import re
import chess.pgn
import io
import helpers
import numpy as np
import itertools


def time_to_sec(time_str):
  return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time_str.split(":"))))

State = namedtuple('state', ['fen', 'move', 'time', 'ev'], verbose=True)
Comment = namedtuple('comment', ['ev', 'time'], verbose=True)

def split_pgn(pgn: str):
  return re.compile("\[Event .*\]").split(pgn)[1:]




def pgn_file_to_array(pgn_file: str):
  arrays = [state_to_data(state) for state in parse_pgn_file(pgn_file)]
  list_xs = [array[0] for array in arrays]
  xs = np.stack(list_xs, axis=0)
  ys = np.stack([array[1] for array in arrays], axis=0)
  return xs, ys


def parse_pgn_file(pgn_file):
  game_states = [parse_game(game_pgn) for game_pgn in split_pgn(pgn_file)]
  return itertools.chain.from_iterable(game_states)

def parse_game(pgn):
  game = chess.pgn.read_game(io.StringIO(pgn))
  board = game.board()
  moves = game.mainline_moves()
  line = game.mainline()

  states = []
  try:
    for x in line:
      fen = x.board().fen()
      move = x.move
      comment = parse_comment(x.comment)
      states.append(State(fen, move, comment.time, comment.ev))
  except ValueError:
    return []

  return states

def parse_comment(comment: str):

  part_time = extract('clk', comment)
  part_eval = extract('eval', comment)
  return Comment(format_eval(part_eval), format_time(part_time))

def extract(name: str, comment: str):
  reg_result = re.search('\[%%%s (.*?)\]' % name, comment)
  if not reg_result:
    return None
  return reg_result.group(0).replace('[%%%s ' % name, '').replace(']', '')

def format_eval(part: str):
  if not part:
    return None
  if '#' in part:
    return None
  return int(float(part) * 100)

def format_time(part: str):
  if not part:
    return None
  return time_to_sec(part)
  

NUM_COLUMNS = 8
NUM_CASTLE_STATES = 4 
NUM_EP_STATES = 1
NUM_COLOR_STATES = 1

PIECES = 'pnbrqk'
ALL_PIECES = PIECES + PIECES.upper()
NUM_PIECES = len(PIECES)
NUM_FEN_DIMENSIONS = (2 * NUM_PIECES) + NUM_CASTLE_STATES + NUM_EP_STATES + NUM_COLOR_STATES

NUM_TIME_DIMENSIONS = 1
NUM_DIMENSIONS = NUM_FEN_DIMENSIONS + NUM_TIME_DIMENSIONS 

def fen_clean(fen):
    cleaned = fen
    for number in range(1, 9):
        cleaned = cleaned.replace(str(number), 'E' * number)
    cleaned = cleaned.replace('/', '')
    assert len(cleaned) == 64
    return cleaned


def fen_to_piece_vector(fen): 
  cleaned = fen_clean(fen)
  
  x = np.zeros((NUM_COLUMNS, NUM_COLUMNS, 2 * NUM_PIECES))
  for i in range(NUM_COLUMNS):
    for j in range(NUM_COLUMNS):
      for k in range(2 * NUM_PIECES):
        x[i][j][k] = cleaned[(7 - i) * 8 + j] == ALL_PIECES[k]

  return x

def fen_to_castle_vector(fen):

  castling_values = 'kQkQ'
  zeros = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_CASTLE_STATES))
  vals_array = np.array([v in fen for v in castling_values])
  return zeros + vals_array


def ep_string_to_position(ep_string: str):
  if ep_string == '-':
    return (0, 0, 0)
  ep_col = helpers.colnames.index(ep_string[0])
  ep_row = int(ep_string[1])
  return (1, ep_col, ep_row)
  
  

def fen_to_enpassant_vector(fen):
  (was_found, col, row) = ep_string_to_position(fen)
  vals = np.zeros((NUM_COLUMNS, NUM_COLUMNS, 1))
  if was_found:
    vals[col][row][0] = 1
  return vals

def fen_to_color_vector(fen):
  vals_array = np.array([1 * (fen != 'w')])
  zeros = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_COLOR_STATES))
  return zeros + vals_array


def fen_to_vector(fen):

  splitted = fen.split(' ')

  fen_pos = splitted[0]
  fen_color = splitted[1]
  fen_castle = splitted[2]
  fen_ep = splitted[3]

  piece_vector = fen_to_piece_vector(fen_pos)
  castle_vector = fen_to_castle_vector(fen_castle)
  enpassant_vector = fen_to_enpassant_vector(fen_ep)
  color_vector = fen_to_color_vector(fen_color)

  return np.concatenate((piece_vector, castle_vector, enpassant_vector, color_vector), axis=2)

def time_to_vector(time):
  return np.random.rand(NUM_COLUMNS, NUM_COLUMNS, NUM_TIME_DIMENSIONS)

all_moves = helpers.all_possible_moves()

def get_move_index(move):
  uci = move.uci()
  return all_moves.index(uci)

def state_to_outcome(state): 
  return get_move_index(state.move)

def state_to_vector(state):
  fen_vector = fen_to_vector(state.fen)
  time_vector = time_to_vector(state.time)
  return np.concatenate((fen_vector, time_vector), axis=2)

def state_to_data(state): 
  x = state_to_vector(state)
  y = np.array([state_to_outcome(state)])
  return (x, y)

