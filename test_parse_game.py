import unittest
import parse_game as parse

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



# [(fen, move, time, ev)] -> predictive model for move:
# move = f(fen, time, stats_players)
# To do it practically, I split out fen into 8x8xZ 
# then add layers for (time, player_stat)
