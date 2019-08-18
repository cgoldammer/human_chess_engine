from __future__ import absolute_import, division, print_function, unicode_literals
import os
import parse_game as parse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

import tensorflow as tf
import helpers
from tensorflow.keras import datasets, layers, models

num_layers = 10

# Model: Input -> [Conv2D() -> BatchNorm -> Activation] -> Flatten -> Output
class Net(object):
  def __init__(self):
    model = models.Sequential()
    input_shape = parse.NUM_COLUMNS, parse.NUM_COLUMNS, parse.NUM_DIMENSIONS

    model.add(layers.Conv2D(num_layers, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization(axis=-1))
    model.add(layers.Activation('relu'))

    model.add(layers.Conv2D(num_layers, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization(axis=-1))
    model.add(layers.Activation('relu'))

    model.add(layers.Flatten())
    model.add(layers.Dense(helpers.EXPECTED_MOVES, activation='softmax'))

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    self.model = model
    self.input_shape = input_shape

  def fit(self, x, y, params, restart=True):
    model = self.model
    model.fit(x, y, **params)
    self.model = model
    return model

  def predict(self, x):
    return self.model.predict(x)
