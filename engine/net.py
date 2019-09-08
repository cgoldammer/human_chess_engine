from __future__ import absolute_import, division, print_function, unicode_literals
import os
import parse_game as parse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

import tensorflow as tf
import helpers
from tensorflow.keras import datasets, layers, models

num_layers_default = 20
layers_multiplier_default = 2
conv_size_default = 3
num_nets_default = 2


# Model: Input -> [Conv2D() -> BatchNorm -> Activation] -> Flatten -> Output
class Net(object):
  def __init__(self, params=None):

    if params:
      num_layers = params.get('num_layers', num_layers_default)
      layers_multiplier = params.get('layers_multiplier', layers_multiplier_default)
      conv_size = params.get('conv_size', conv_size_default)
      num_nets = params.get('num_nets', num_nets_default)

    model = models.Sequential()
    input_shape = parse.NUM_COLUMNS, parse.NUM_COLUMNS, parse.NUM_DIMENSIONS

    conv_shape = conv_size, conv_size

    model.add(layers.Conv2D(num_layers, conv_shape, activation='relu', padding='same', input_shape=input_shape))
    model.add(layers.BatchNormalization(axis=-1))
    model.add(layers.Activation('relu'))

    for i in range(num_nets):
        model.add(layers.Conv2D(num_layers * layers_multiplier, conv_shape, padding='same', activation='relu'))
        model.add(layers.BatchNormalization(axis=-1))
        model.add(layers.Activation('relu'))

    model.add(layers.Flatten())
    model.add(layers.Dense(helpers.EXPECTED_MOVES, activation='softmax'))

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    self.model = model
    self.input_shape = input_shape

  def fit(self, x, y, params=None, restart=True):
    if not params:
      params = {}

    model = self.model
    model.fit(x, y, **params)
    self.model = model
    return model

  def predict(self, x):
    return self.model.predict(x)
