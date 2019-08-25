import numpy as np
import parse_game as p
import net as net_module
import pandas as pd
import helpers
import imp
from sys import getsizeof

POS_COLOR = (2 * p.NUM_PIECES)

pgn = open('data/test/many_games.pgn').read()

char_per_move = 31
num_moves_thousand = 500

%time x, y = p.pgn_file_to_array(pgn[0: num_moves_thousand * char_per_move * 1000])
x.shape
getsizeof(x) / 10**6

num_initial = x.shape[0]
num_initial

random_ix = np.random.choice(num_initial, num_initial, replace=False)
x_rand = x[random_ix, :]
y_rand = y[random_ix, :]
assert x_rand.shape == x.shape

# ix = x_rand[:, 0, 0, POS_COLOR] == 1
# x_rand = x_rand[ix]
# y_rand = y_rand[ix]

n = x_rand.shape[0]
share_train = 0.95
ix = np.random.random(n) < share_train

x_train = x_rand[ix]
y_train = y_rand[ix]
x_test = x_rand[~ix]
y_test = y_rand[~ix]

x_train.shape

params_net = {
  'num_layers': 5,
  'layers_multiplier': 1,
  'conv_size': 3
}
net = net_module.Net(params_net)
net.model.summary()

params_fit = {
  'epochs': 2,
  'validation_data': (x_test, y_test),
  'batch_size': 1000,
  'verbose': 1
}
%time net.fit(x_train, y_train, params_fit)


y_hat = net.predict(x_test)
df = pd.DataFrame(y_test)
df.columns = ['y']
df['y_hat'] = y_hat.argmax(axis=1)
df['y_hat_prob'] = y_hat.max(axis=1)
df['match'] = df.y == df.y_hat
df['y_hat_naive'] = df.y.mode().loc[0]
df['match_naive'] = df.y == df.y_hat_naive

all_moves = helpers.all_possible_moves()
df['move'] = [all_moves[i] for i in df.y]
df['move_hat'] = [all_moves[i] for i in df.y_hat]
df['fen'] = [p.vector_to_fen(v) for v in x_test]
df['rating_white'] = [p.vector_to_rating(v)[0] for v in x_test]
df['rating_black'] = [p.vector_to_rating(v)[1] for v in x_test]

pd.set_option('display.max_colwidth', 100)
df[['fen', 'rating_white', 'rating_black', 'move', 'move_hat', 'y_hat_prob', 'match']].sample(20)

df[['match', 'match_naive']].mean()


fen = '8/8/2kp4/4p3/8/8/8/2K5 w - -'

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

fen = 'rn1qkbnr/pp2pppp/2p5/5b2/3PN3/8/PPP2PPP/R1BQKBNR w KQkq - 1 5'

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
rating = 2500


def get_probs(fen, rating):
  state = p.StateFull(fen=fen, move=None, time=10, ev=None, rating_white=rating, rating_black=rating, total_time=300, increment=5)
  x = p.state_to_vector(state)
  d = pd.DataFrame(net.predict(x.reshape((1, 8, 8, p.NUM_DIMENSIONS)))[0]) * 100
  d.columns = ['prob']
  d['rating'] = rating
  d['fen'] = fen
  d['move'] = all_moves
  d = d.set_index('move')
  return d

ratings = np.arange(500, 4500, 500)

fen = 'rnbqkb1r/5ppp/p2ppn2/6B1/1p2P3/2NB1N2/PPP2PPP/R2QK2R w KQkq - 0 9'
dfs = pd.concat([get_probs(fen, rating) for rating in ratings])
probs = dfs.reset_index().groupby(['move', 'rating']).prob.mean().unstack(1).sort_values(2000, ascending=False)
probs.head(10)



dfs.head(1)


dfs.loc['c4c5'][['rating', 'prob']]
dfs.loc['f7f6'][['rating', 'prob']]

dfs.loc['e2e4'][['rating', 'prob']]
dfs.loc['c2c4'][['rating', 'prob']]


dfs.loc['g1f3'][['rating', 'prob']]




pd.set_option('display.precision', 1)
d1 = get_probs(fen, 100)
d2 = get_probs(fen, 2000)
d3 = get_probs(fen, 3000)
d1['prob_2000'] = d2
d1['prob_3000'] = d3
d1.sort_values('prob_2000', ascending=False).head(10) * 100






pg = open('data/test/one_game.pgn').read()
parsed = p.parse_game(pg)
parsed

p.standardize_state(parsed[0])
parsed[1]
p.standardize_state(parsed[1])

p.standardize_state(parsed[2])
parsed[3]
p.standardize_state(parsed[3])

parsed[5]
p.standardize_state(parsed[5])

game = chess.pgn.read_game(io.StringIO(pgn))

pgn = '1.e4 { [%clk 0:00:05] } e5 { [%clk 0:00:10] }'

import parse_game as p
x, y = p.state_to_data(parsed[0])
x, y = p.state_to_data(parsed[0])
x.shape

p.positions

parsed[0]
parsed[1]

p.vector_to_fen(p.state_to_data(parsed[0])[0])
p.vector_to_fen(p.state_to_data(parsed[1])[0])


p.state_to_data(parsed[0])[0][0][0][12:13]
p.state_to_data(parsed[1])[0][0][0][12:13]

d = p.state_to_data(parsed[1])[0]
d[0][0][12:13]
d.sum()
p.vector_to_fen(d)
d.sum()
d[0][0][12:13]

p.fen_to_vector('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1')[0][0][12:13]



