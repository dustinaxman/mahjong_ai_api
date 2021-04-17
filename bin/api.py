#!/usr/bin/env python
from mahjong_ai import Game, Environment, Player, TILES, InteractiveGame
from flask import Flask, request
from flask_restful import Resource, Api
import json
from pathlib import Path

MODEL_SAVE_DIR=Path().home()/'mahjong/games/'
MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)
cached_game_json = MODEL_SAVE_DIR/'cached_game.json'

app = Flask(__name__)
api = Api(app)

def load_cached_game():
    loaded_game = Game(player_list=[Player() for _ in range(4)])
    loaded_game.from_json(cached_game_json)
    ig = InteractiveGame(game=loaded_game)
    return ig


def save_cached_game(ig):
    cached_game_json.unlink(missing_ok=True)
    ig.g.to_json(cached_game_json)


class GetGameState(Resource):
    def get(self):
        ig = load_cached_game()
        return {'game_dict': ig.g.to_dict()}


class StartGame(Resource):
    def post(self, starting_player_idx):
        print(json.loads(request.form['my_hand']))
        my_hand = [tuple(tile) for tile in json.loads(request.form['my_hand'])]
        ig = InteractiveGame(starting_player_idx=starting_player_idx, my_hand=my_hand)
        save_cached_game(ig)
        return {'game_dict': ig.g.to_dict()}


class Pong(Resource):
    def post(self, pong_player_idx):
        ig = load_cached_game()
        tile_list = [tuple(tile) for tile in json.loads(request.form['tile_list'])]
        ig.pong(pong_player_idx, tile_list)
        save_cached_game(ig)


class GetChiRecommendation(Resource):
    def get(self):
        ig = load_cached_game()
        tiles_opened = ig.get_chi_recommendation()
        save_cached_game(ig)
        return {'tiles_opened': tiles_opened}


class Discard(Resource):
    def post(self):
        ig = load_cached_game()
        tile = json.loads(request.form['tile'])
        if tile is not None:
            tile = tuple(tile)
        discarded_or_opened = ig.discard(tile)
        save_cached_game(ig)
        return {'discarded_or_opened': discarded_or_opened}


class Chi(Resource):
    def post(self):
        ig = load_cached_game()
        tile_list = [tuple(tile) for tile in json.loads(request.form['tile_list'])]
        ig.chi(tile_list)
        save_cached_game(ig)


class Pickup(Resource):
    def post(self):
        ig = load_cached_game()
        tile = tuple(json.loads(request.form['tile']))
        ig.pickup(tile)
        save_cached_game(ig)


api.add_resource(GetGameState, '/get-game-state')
api.add_resource(StartGame, '/start-game/<int:starting_player_idx>')
api.add_resource(Pong, '/pong/<int:pong_player_idx>')
api.add_resource(GetChiRecommendation, '/get-chi-recommendation')
api.add_resource(Discard, '/discard')
api.add_resource(Chi, '/chi')
api.add_resource(Pickup, '/pickup')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)



