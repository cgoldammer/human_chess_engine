import unittest
import helpers

all_moves = helpers.all_possible_moves()

class TestHelpers(unittest.TestCase):
  def test_rook_moves(self):
    rook_move_legal = helpers.is_rook_move(1, 1, 2, 1)
    self.assertTrue(rook_move_legal)

    rook_move_illegal = helpers.is_rook_move(1, 2, 3, 4)
    self.assertFalse(rook_move_illegal)

  def test_bishop_moves(self):
    bishop_move_legal = helpers.is_bishop_move(1, 1, 2, 2)
    self.assertTrue(bishop_move_legal)

    bishop_move_legal = helpers.is_bishop_move(1, 8, 2, 7)
    self.assertTrue(bishop_move_legal)

    bishop_move_illegal = helpers.is_bishop_move(1, 1, 3, 4)
    self.assertFalse(bishop_move_illegal)

  def test_knight_moves(self):
    knight_move_legal = helpers.is_knight_move(1, 1, 2, 3)
    self.assertTrue(knight_move_legal)

    knight_move_legal = helpers.is_knight_move(1, 1, 3, 2)
    self.assertTrue(knight_move_legal)

    knight_move_illegal = helpers.is_knight_move(1, 1, 3, 3)
    self.assertFalse(knight_move_illegal)

  def test_all_possible_moves(self):
    EXPECTED_MOVES = 1968
    self.assertEqual(len(all_moves), EXPECTED_MOVES)
