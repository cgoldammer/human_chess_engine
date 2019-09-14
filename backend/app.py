from flask import Flask, escape, request
import boto3
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from engine import parse_game as parse
from flask_restful import Resource, Api
import urllib


app = Flask(__name__)
api = Api(app)

model = keras.models.load_model('moves.h5')



class Probs(Resource):
  def get(self, fen, total_time, increment, time, rating_white, rating_black):
    print(fen)
    f = fen.replace('+', ' ').replace('S', '/')
    params = {
      'fen': f,
      'time': time,
      'rating_white': rating_white,
      'rating_black': rating_black,
      'total_time': total_time,
      'increment': increment,
      'move': None,
      'ev': None
    }

    st = parse.StateFull(**params)
    x = parse.state_to_vector(st)
    new_shape = tuple([1] + list(x.shape))

    probs = model.predict(x.reshape(new_shape))[0, :]
    s = pd.Series(probs)
    s.index = parse.all_moves

    d = s.sort_values(ascending=False).to_dict()
    l = [[k, v] for (k, v) in d.items()]

    return l

url = '/human_api/fen=<string:fen>'
url += '/totaltime=<int:total_time>'
url += '/increment=<int:increment>'
url += '/time=<int:time>'
url += '/ratingwhite=<int:rating_white>'
url += '/ratingblack=<int:rating_black>'
api.add_resource(Probs, url)

