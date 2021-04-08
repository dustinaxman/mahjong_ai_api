#!/usr/bin/env python
from mahjong_ai import Game, Environment, Player, TILES
from flask import Flask, request
from flask_restful import Resource, Api
import json


app = Flask(__name__)
api = Api(app)
g = Game(player_list=[Player() for _ in range(4)])

class UpdateGame(Resource):
    def patch(self):
        game_state_dict = json.loads(request.form['game_state'])
        g.from_dict(game_state_dict)
        return game_state_dict

class Chi(Resource):
    def get(self):
        tiles_opened = g.player_list[g.env.current_player_idx].do_chi(g)
        return {'tiles_opened': tiles_opened}

class Pong(Resource):
    def get(self, pong_player_idx):
        tiles_opened = g.player_list[g.env.current_player_idx].do_pong(g, pong_player_idx)
        return {'tiles_opened': tiles_opened}

class Discard(Resource):
    def get(self):
        print(g.env.current_player_idx)
        print(g.player_list[g.env.current_player_idx].hand)
        discard_tile = g.player_list[g.env.current_player_idx].discard(g)
        return {'discard_tile': discard_tile}


api.add_resource(UpdateGame, '/update-game')
api.add_resource(Chi, '/chi')
api.add_resource(Pong, '/pong/<int:pong_player_idx>')
api.add_resource(Discard, '/discard')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)





