from collections import namedtuple
import re
import chess.pgn
import io


def time_to_sec(time_str):
  return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time_str.split(":"))))

State = namedtuple('state', ['fen', 'move', 'time', 'ev'], verbose=True)
Comment = namedtuple('comment', ['ev', 'time'], verbose=True)

def parse_game(pgn: str):
  print(pgn)
  game = chess.pgn.read_game(io.StringIO(pgn))


  board = game.board()
  moves = game.mainline_moves()
  line = game.mainline()

  states = []
  for x in line:
    fen = x.board().board_fen()
    move = x.move
    comment = parse_comment(x.comment)
    states.append(State(fen, move, comment.time, comment.ev))

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
  return int(float(part) * 100)

def format_time(part: str):
  if not part:
    return None
  return time_to_sec(part)
  
  





