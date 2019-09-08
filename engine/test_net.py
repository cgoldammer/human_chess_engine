import unittest
import net as net_module
import numpy as np
import parse_game as parse
import helpers

class TestNet(unittest.TestCase):
  def test_fake(self):
    net = net_module.Net()
    NUM_OBS = 1000
    shape_input = (NUM_OBS, parse.NUM_COLUMNS, parse.NUM_COLUMNS, parse.NUM_DIMENSIONS)
    shape_output = (NUM_OBS, helpers.EXPECTED_MOVES)

    x_fake = np.random.random(shape_input)
    y_fake = np.random.randint(0, helpers.EXPECTED_MOVES, size=NUM_OBS)

    net.fit(x_fake, y_fake)
    y_hat = net.predict(x_fake)
    self.assertTrue(1, 0)

    self.assertEqual(y_hat.shape, shape_output)


class TestPipeline(unittest.TestCase):
  def simple_test(self):
    pgn = open('data/test/sample_eval.pgn').read()
    x, y = parse.pgn_file_to_array(pgn)

    (num_states, cols1, cols2, layers) = x.shape
    dim_result = (cols1, cols2, layers)
    dim_expected = (parse.NUM_COLUMNS, parse.NUM_COLUMNS, parse.NUM_DIMENSIONS)
    self.assertEqual(dim_result, dim_expected)

    net = net_module.Net()
    net.fit(x, y)
    y_hat = net.predict(x)

    self.assertEqual(y_hat.shape, (num_states, helpers.EXPECTED_MOVES))


