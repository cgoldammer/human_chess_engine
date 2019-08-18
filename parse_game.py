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

  current_board = board

  states = []
  try:
    for x in line:
      move = x.move
      comment = parse_comment(x.comment)
      states.append(State(current_board.fen(), move, comment.time, comment.ev))
      current_board = x.board()
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
CASTLING_VALUES = 'KQkq'
NUM_CASTLE_STATES = len(CASTLING_VALUES)
NUM_EP_STATES = 1
NUM_COLOR_STATES = 1
NUM_HALFMOVE_STATES = 2

PIECES = 'pnbrqk'
ALL_PIECES = PIECES + PIECES.upper()
NUM_PIECES = len(PIECES)
NUM_FEN_DIMENSIONS = (2 * NUM_PIECES) + NUM_CASTLE_STATES + NUM_EP_STATES + NUM_COLOR_STATES + NUM_HALFMOVE_STATES

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

def fen_to_halfmove_vector(fen1, fen2):
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
  fen_halfmoves = splitted[4], splitted[5]

  piece_vector = fen_to_piece_vector(fen_pos)
  castle_vector = fen_to_castle_vector(fen_castle)
  ep_vector = fen_to_ep_vector(fen_ep)

  color_vector = fen_to_color_vector(fen_color)
  halfmove_vector = fen_to_halfmove_vector(*fen_halfmoves)

  return np.concatenate((piece_vector, color_vector, castle_vector, ep_vector, halfmove_vector), axis=2)

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
  is_white = color_vector[0][0] = 1
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

def halfmove_vector_to_fen(halfmove_vector):
  return '%s %s' % (int(halfmove_vector[0][0][0]), int(halfmove_vector[0][0][1]))


def vector_to_fen(vec):

  pos = 0
  length = 2 * NUM_PIECES
  fen_piece = piece_vector_to_fen(vec[:, :, pos: pos+length])

  pos += length
  length = NUM_COLOR_STATES
  fen_color = color_vector_to_fen(vec[:, :, pos: pos+length])
  
  pos += length
  length = NUM_CASTLE_STATES
  fen_castle = castle_vector_to_fen(vec[:, :, pos: pos+length])

  pos += length
  length = NUM_EP_STATES
  fen_ep = ep_vector_to_fen(vec[:, :, pos: pos+length])

  pos += length
  length = NUM_HALFMOVE_STATES
  fen_halfmove = halfmove_vector_to_fen(vec[:, :, pos: pos+length])

  fen = "%s %s %s %s %s" % (fen_piece, fen_color, fen_castle, fen_ep, fen_halfmove)

  return fen



  
  
