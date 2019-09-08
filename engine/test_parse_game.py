import unittest
import parse_game as parse
import numpy as np
import net as net_module

class TestParse(unittest.TestCase):
  def test_parse(self):
    """Testing that I can parse the game"""
    pgn = '1.e4 { [%clk 0:00:05] } e5 { [%clk 0:00:10] }'
    parsed = parse.parse_game(pgn)
    self.assertEqual(len(parsed), 2)
    self.assertEqual([s.time for s in parsed], [5, 10])

  def test_parse_comments(self):
    comment = "[%eval -2.73] [%clk 0:00:21]"
    results = parse.parse_comment(comment)
    self.assertEqual(results, parse.Comment(-273, 21))

  def test_parse_comments(self):
    comment = "[%clk 0:00:21]"
    results = parse.parse_comment(comment)
    self.assertEqual(results, parse.Comment(None, 21))

  def test_parse_eval(self):
    part = '2.73'
    result = parse.format_eval(part)
    self.assertEqual(result, 273)

  def test_parse_time(self):
    part = '1:00:21'
    result = parse.format_time(part)
    self.assertEqual(result, 60 * 60 + 21)

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

position_rook_white = parse.PIECES.index('r')
position_rook_black = position_rook_white + parse.NUM_PIECES

class TestVectorize(unittest.TestCase):
  def test_fen_to_vector(self): 
    v = parse.fen_to_vector(STARTING_FEN)
    self.assertEqual(v.shape, (8, 8, parse.NUM_FEN_DIMENSIONS))

  def test_fen_to_piece_vector(self): 
    v = parse.fen_to_piece_vector(STARTING_FEN.split(' ')[0])
    self.assertEqual(v[parse.NUM_COLUMNS - 1][0][position_rook_white], 1)
    self.assertEqual(v[parse.NUM_COLUMNS - 1][0][position_rook_black], 0)
    self.assertEqual(v[0][0][position_rook_black], 1)
    self.assertEqual(v[0][0][position_rook_white], 0)

  def test_fen_to_color_vector(self): 
    v = parse.fen_to_color_vector('w')
    self.assertEqual(v[0][0][0], 1)

    v = parse.fen_to_color_vector('b')
    self.assertEqual(v[0][0][0], 0)

  def test_fen_to_castle_vector(self): 
    v = parse.fen_to_castle_vector('kqKQ')
    self.assertEqual(list(v[0][0]), [1, 1, 1, 1])

    v = parse.fen_to_castle_vector('-')
    self.assertEqual(list(v[0][0]), [0, 0, 0, 0])


class TestToFen(unittest.TestCase):

  def test_castle_vector_to_fen(self):
    fen = 'KQkq'
    castle_vector = parse.fen_to_castle_vector(fen)
    fen_back = parse.castle_vector_to_fen(castle_vector)
    self.assertEqual(fen, fen_back)

  def test_ep_vector_to_fen(self):
    fen = 'e3'
    ep_vector = parse.fen_to_ep_vector(fen)
    fen_back = parse.ep_vector_to_fen(ep_vector)
    self.assertEqual(fen, fen_back)

    fen = '-'
    ep_vector = parse.fen_to_ep_vector(fen)
    fen_back = parse.ep_vector_to_fen(ep_vector)
    self.assertEqual(fen, fen_back)

  def test_piece_vector_to_fen(self):
    fen = 'rnbqk2r/ppppp1bp/5np1/5p2/2PP4/5NP1/PP2PPBP/RNBQK2R'
    piece_vector = parse.fen_to_piece_vector(fen)
    fen_back = parse.piece_vector_to_fen(piece_vector)
    self.assertEqual(fen, fen_back)

  def test_fen_vector_to_fen(self):
    fens = [
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    ]

    for fen in fens:
      fen_vector = parse.fen_to_vector(fen)
      fen_back = parse.vector_to_fen(fen_vector)
      self.assertEqual(fen, fen_back)

fen_white = 'rnbqkb1r/pppp1ppp/4pn2/8/1PP5/2N5/P2PPPPP/R1BQKBNR b KQkq - 2 3'
fen_invert_pos = 'r1bqkbnr/p2ppppp/2n5/1pp5/8/4PN2/PPPP1PPP/RNBQKB1R b kqKQ - 2 3'

class TestInvert(unittest.TestCase):
  def test_invert_move(self):
    uci = 'd3d6'
    expected = 'd6d3'
    self.assertEqual(parse.invert_move(uci), expected)

    uci = 'd7d8N'
    expected = 'd2d1N'
    self.assertEqual(parse.invert_move(uci), expected)

  def test_invert_fen(self):
    self.assertEqual(parse.invert_fen(fen_white), fen_invert_pos)

