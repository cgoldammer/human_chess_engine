from collections import namedtuple
import re
import chess.pgn
import io
import numpy as np
import itertools
import engine.helpers as helpers


def time_to_sec(time_str):
  return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time_str.split(":"))))

GameStats = namedtuple('gamestats', ['rating_white', 'rating_black', 'total_time', 'increment'])
State = namedtuple('state', ['fen', 'move', 'time', 'ev'])

state_cols = ['fen', 'move', 'time', 'ev', 'rating_white', 'rating_black', 'total_time', 'increment']
StateFull = namedtuple('state', state_cols)
Comment = namedtuple('comment', ['ev', 'time'])
Range = namedtuple('range', ['start', 'end'])

def split_pgn(pgn: str):
  return re.compile("\[Event .*\]").split(pgn)[1:]

def pgn_file_to_array(pgn_file: str):
  arrays = [state_to_data(state) for state in parse_pgn_file(pgn_file)]
  list_xs = [array[0] for array in arrays]
  try:
      xs = np.stack(list_xs, axis=0)
      ys = np.stack([array[1] for array in arrays], axis=0)
      return xs, ys
  except ValueError:
      return None, None


def parse_time_control(time_control_string: str):
  split = time_control_string.split('+')
  try:
    total_time = int(split[0])
    increment = int(split[1])
  except ValueError:
    return None
  return (total_time / TIME_STANDARDIZER, increment / TIME_STANDARDIZER)


def parse_pgn_file(pgn_file):
  game_states = [parse_game(game_pgn) for game_pgn in split_pgn(pgn_file)]

  return itertools.chain.from_iterable(game_states)

def parse_game(pgn):
  game = chess.pgn.read_game(io.StringIO(pgn))

  headers = game.headers

  try:
    rating_white = int(headers['WhiteElo'])
  except (KeyError, ValueError):
    rating_white = None
  try:
    rating_black = int(headers['BlackElo'])
  except (KeyError, ValueError):
    rating_black = None
  try:
    (total_time, increment) = parse_time_control(headers['TimeControl'])
  except (KeyError, ValueError, TypeError):
    (total_time, increment) = (None, None)

  board = game.board()
  moves = game.mainline_moves()
  line = game.mainline()

  current_board = board

  states = []
  try:
    for x in line:
      move = x.move.uci()
      comment = parse_comment(x.comment)
      states.append(StateFull(
        current_board.fen(), move, comment.time, comment.ev,
        rating_white, rating_black, total_time, increment))
      current_board = x.board()
  except ValueError:
    return None

  return states

def parse_comment(comment: str):
  part_time = extract('clk', comment) / TIME_STANDARDIZER
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
CASTLING_VALUES = 'KQkq'
NUM_CASTLE_STATES = len(CASTLING_VALUES)
NUM_EP_STATES = 1
NUM_COLOR_STATES = 1
NUM_HALFMOVE_STATES = 2

PIECES = 'pnbrqk'
ALL_PIECES = PIECES + PIECES.upper()
NUM_PIECES = len(PIECES)
NUM_ALL_PIECES = len(ALL_PIECES)
NUM_TIME_DIMENSIONS = 3
NUM_RATING_DIMENSIONS = 2

fen_components = ['position', 'color', 'castle', 'ep'] #, 'half_move']

components = {
  'position': NUM_ALL_PIECES,
  'color': NUM_COLOR_STATES,
  'castle': NUM_CASTLE_STATES,
  'ep': NUM_EP_STATES,
  #'half_move': NUM_HALFMOVE_STATES,
  'time': NUM_TIME_DIMENSIONS,
  'rating': NUM_RATING_DIMENSIONS
}

NUM_FEN_DIMENSIONS = sum([n for (k, n) in components.items() if k in fen_components])
NUM_DIMENSIONS = sum(components.values())

def get_positions():
  positions = {}
  start_pos = 0
  for (component, num) in components.items():
    end_pos = start_pos + num
    positions[component] = Range(start=start_pos, end=end_pos)
    start_pos = end_pos
  return positions

positions = get_positions()

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
  zeros = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_CASTLE_STATES))
  vals_array = np.array([v in fen for v in CASTLING_VALUES])
  return zeros + vals_array

def ep_string_to_position(ep_string: str):
  if ep_string == '-':
    return (0, 0, 0)
  ep_col = helpers.colnames.index(ep_string[0])
  ep_row = int(ep_string[1]) - 1
  return (1, ep_col, ep_row)
  
def fen_to_ep_vector(fen):
  (was_found, col, row) = ep_string_to_position(fen)
  vals = np.zeros((NUM_COLUMNS, NUM_COLUMNS, 1))
  if was_found:
    vals[col][row][0] = 1
  return vals

def fen_to_color_vector(fen):
  vals_array = np.array([1 * (fen == 'w')])
  zeros = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_COLOR_STATES))
  return zeros + vals_array

def fen_to_half_move_vector(fen1, fen2):
  h1, h2 = int(fen1), int(fen2)
  vec = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_HALFMOVE_STATES))
  vec[:, :, 0] = h1
  vec[:, :, 1] = h2
  return vec

def fen_to_vector(fen):

  splitted = fen.split(' ')

  fen_pos = splitted[0]
  fen_color = splitted[1]
  fen_castle = splitted[2]
  fen_ep = splitted[3]
  fen_half_move = splitted[4], splitted[5]

  piece_vector = fen_to_piece_vector(fen_pos)
  castle_vector = fen_to_castle_vector(fen_castle)
  ep_vector = fen_to_ep_vector(fen_ep)

  color_vector = fen_to_color_vector(fen_color)
  half_move_vector = fen_to_half_move_vector(*fen_half_move)

  return np.concatenate((piece_vector, color_vector, castle_vector, ep_vector), axis=2)


TIME_STANDARDIZER = 1000

def time_to_vector(time):
  return np.random.rand(NUM_COLUMNS, NUM_COLUMNS, NUM_TIME_DIMENSIONS)

all_moves = helpers.all_possible_moves()

def invert_move(uci):
  # We replace all numbers by their inverse on the board, e.g. 8 with 1 and 2 with 7

  for i in range(1, 9):
    uci = uci.replace(str(i), 'A%s' % i)

  for i in range(1, 9):
    uci = uci.replace('A%s' % i, 'Z%s' % (9 - i))

  for i in range(1, 9):
    uci = uci.replace('Z%s' % i, str(i))

  return uci



def get_move_index(move):
  return all_moves.index(move)

def state_to_outcome(state): 
  return get_move_index(state.move)


RATING_STANDARDIZER = 3000

def rating_to_vector(white_to_move, rating_white, rating_black):
  values = [rating_white, rating_black] if white_to_move else [rating_black, rating_white]
  zeros = np.zeros((NUM_COLUMNS, NUM_COLUMNS, NUM_RATING_DIMENSIONS))
  vals_array = np.array(values) / RATING_STANDARDIZER
  return zeros + vals_array

def state_to_vector(state):
  fen = state.fen
  white_to_move = 'w' in fen
  fen_vector = fen_to_vector(state.fen)
  time_vector = time_to_vector(state.time)
  rating_vector = rating_to_vector(white_to_move, state.rating_white, state.rating_black)
  return np.concatenate((fen_vector, time_vector, rating_vector), axis=2)

def invert_color(fen_pos: str):
  for piece in PIECES:
    fen_pos = (fen_pos
        .replace(piece.upper(), 'T')
        .replace(piece, piece.upper())
        .replace('T', piece))
  return fen_pos


def invert_ep(fen_ep):
  if fen_ep == '-':
    return fen_ep
  col = fen_ep[0]
  row = fen_ep[1]

  return '%s%s' % (col, 9-int(row))

def invert_castle(fen_castle):
  return invert_color(fen_castle)

def invert_pos(fen_pos): 

  for piece in PIECES:
    fen_pos = (fen_pos
        .replace(piece.upper(), 'T')
        .replace(piece, piece.upper())
        .replace('T', piece))

  rows = fen_pos.split('/')
  rows_inverted = rows[::-1]

  return '/'.join(rows_inverted)

def invert_fen(fen: str):
  splitted = fen.split(' ')

  fen_pos = splitted[0]
  fen_color = splitted[1]
  fen_castle = splitted[2]
  fen_ep = splitted[3]
  half_move_1, half_move_2 = splitted[4], splitted[5]

  fen_ep_inverted = invert_ep(fen_ep)
  fen_castle_inverted = invert_castle(fen_castle)
  fen_pos_inverted = invert_pos(fen_pos)

  values = (fen_pos_inverted, fen_color, fen_castle_inverted, fen_ep_inverted, half_move_1, half_move_2)
  inverted = '%s %s %s %s %s %s' % values

  return inverted

def invert_state(state):
  fen = state.fen

  state_new = StateFull(
      fen=invert_fen(fen),
      move=invert_move(state.move),
      time=state.time,
      ev=state.ev,
      rating_white=state.rating_white,
      rating_black=state.rating_black,
      total_time=state.total_time,
      increment=state.increment)

  return state_new


def standardize_state(state):
  is_white = 'w' in state.fen
  return state if is_white else invert_state(state)


def state_to_data(state): 
  # We are always expressing the board from the white player's
  # viewpoint.  Thus, if it's black to move, we invert the fen.
  x = state_to_vector(state)
  y = np.array([state_to_outcome(state)])
  return (x, y)


def piece_vector_to_fen(piece_vector):
  fen_string = ''
  for row in range(NUM_COLUMNS)[::-1]:
    missing_count = 0
    for col in range(NUM_COLUMNS):
      if piece_vector[row, col].max() == 0:
        missing_count += 1
        continue
      for i, piece in enumerate(ALL_PIECES):
        if piece_vector[row, col, i] == 1:
          if missing_count > 0:
            fen_string += str(missing_count)
            missing_count = 0
          fen_string += piece
    if missing_count > 0:
      fen_string += str(missing_count)
      missing_count = 0
    if row >= 1:
      fen_string += "/"
  return fen_string


def color_vector_to_fen(color_vector):
  is_white = color_vector[0][0][0] == 1
  return 'w' if is_white else 'b'

def castle_vector_to_fen(castle_vector):
  castling_fen = ''
  for i, value in enumerate(CASTLING_VALUES):
    if castle_vector[0][0][i] == 1:
      castling_fen += value
  if castling_fen == '':
    castling_fen = '-'
  return castling_fen

COLUMN_NAMES = 'abcdefgh'
def ep_vector_to_fen(ep_vector):
  fen = '-'
  for i, col_name in enumerate(COLUMN_NAMES):
    for j in range(NUM_COLUMNS):
      if ep_vector[i, j] == 1:
        fen = '%s%s' % (col_name, j+1)
  return fen

def half_move_vector_to_fen(half_move_vector):
  return '%s %s' % (int(half_move_vector[0][0][0]), int(half_move_vector[0][0][1]))

def get_by_range(vec, r):
  return vec[:, :, r.start: r.end]

def vector_to_rating(vec):
  return (get_by_range(vec, positions['rating'])[0][0] * RATING_STANDARDIZER).astype(int)


def vector_to_fen(vec):
  fen_piece = piece_vector_to_fen(get_by_range(vec, positions['position']))
  fen_color = color_vector_to_fen(get_by_range(vec, positions['color']))
  fen_castle = castle_vector_to_fen(get_by_range(vec, positions['castle']))
  fen_ep = ep_vector_to_fen(get_by_range(vec, positions['ep']))

  # fen_half_move = half_move_vector_to_fen(get_by_range(vec, positions['half_move']))
  fen_half_move = "0 1"
  fen = "%s %s %s %s %s" % (fen_piece, fen_color, fen_castle, fen_ep, fen_half_move)

  is_white = fen_color = 'w'
  if not is_white:
    fen = invert_fen(fen)

  return fen



  
  
