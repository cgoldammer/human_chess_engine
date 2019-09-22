# Human chess engine

This is aiming to build a chess engine that plays like a human. To do this, we train a neural network on millions of games played on Lichess. The network predicts the move probabilities for all theoretically possible moves.

## Features so far

- The algorithm learns sensible moves, and almost always plays legal moves
- Accuracy is 45%: In other words, 45% of the time, the algorithm correctly predicts the move played by the human player.
- Frontend to see the move probabilities: See [code](./frontend) or the [live app](https://chessinsights.org/human)

## Network architecture

Input: All lichess games from 2017-04 (11M games, 25 GB pgn)
Output: Move prediction for all possible 1968 moves.

- Input: (Fen + Game data) 
- Encode as (8,8,23)
- 200 layers
- 5 blocks of [Conv2D, BatchNorm, Activation]
- Flatten
- Dropout
- Softmax of 1968 (all possible moves)

The input features are:
- 10 pieces (5 for white, 5 for black)
- 4 castling states
- 1 en passant state
- 1 state for the color to move
- 2 for halfmoves
- 3 for the game time (total time, time left, increment)
- 2 for the rating

Training time: Roughly 5h on a GTX 1080. 

I've tried a variety of architectures, this performs best so far.

## Biggest problem: Playing strength is low

Even though the algorithm plays moves that are positionally plausible, especially in quiet positions, the algorithm will still commit heavy blunders, for instance by hanging a mate in one move. This is not shocking: Comparable network architectures (e.g. Alpha or Leela Zero) require substantial computational time until they achieve grandmaster-level performance. The algorithm is under heavy development, and over the next months, we aim to evaluate a wide number of networks.

Feedback much appreciated!

## Use cases

- Play against a computer that feels more human-like
- Understand how human play changes as their playing strength increases

## Todo

- Large number of improvements of network structure
  - Resnet
  - Using past game states
- Estimate model for win probability
  - Provide human evaluations for commonly played openings
  - Find positions where a human is likely to blunder
- Simulate the playing styles of various players, e.g. Capablanca vs Tal.
