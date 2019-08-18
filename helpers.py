from itertools import product
EXPECTED_MOVES = 1968

ranks = range(8)
columns = range(8)
colnames = 'abcdefgh'

def col(col_num: int):
  return colnames[col_num]

def all_possible_moves():

  all_moves = product(columns, ranks, columns, ranks)

  legal_moves = []

  for (c_from, r_from, c_to, r_to) in all_moves:
    move = (c_from, r_from, c_to, r_to)
    same_column = c_from == c_to
    same_row = r_from == r_to
    if same_column and same_row:
      continue

    if is_bishop_move(*move) or is_rook_move(*move) or is_knight_move(*move):
      legal_moves.append((c_from, r_from, c_to, r_to, ''))

  legal_moves += pawn_promotion_moves()

  return ['%s%s%s%s%s' % (col(c_from), r_from + 1, col(c_to), r_to + 1, piece) 
      for (c_from, r_from, c_to, r_to, piece) in legal_moves]


def is_bishop_move(c_from, r_from, c_to, r_to):
  row_change = abs(c_from - c_to)
  col_change = abs(r_from - r_to)
  return row_change == col_change

def is_rook_move(c_from, r_from, c_to, r_to):
  return c_from == c_to or r_from == r_to

def is_knight_move(c_from, r_from, c_to, r_to):
  row_change = abs(c_from - c_to)
  col_change = abs(r_from - r_to)
  return (row_change == 2 and col_change == 1) or (row_change == 1 and col_change == 2)

def promotions_by_row(row_from, row_to): 
  pieces = 'qrbn'
  return [(c, row_from, c + col_change, row_to, piece) 
      for c in columns 
      for col_change in [-1, 0, 1]
      for piece in pieces
      if 0 <= c + col_change <= 7]

def pawn_promotion_moves():
  return promotions_by_row(6, 7) + promotions_by_row(1, 0)
