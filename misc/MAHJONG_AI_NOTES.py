hand =TILES
def open_group(tile_list, type_of_match, hand):
	tile_set = set(tile_list)
	count = 0
	open_groups = []
	new_hand = []
	for tile in hand:
		if type_of_match == 'flush':
			if tile in tile_set and not count == 3:
				count += 1
			else:
				new_hand.append(tile)
		else:
			if tile in tile_set:
				tile_set.remove(tile)
			else:
				new_hand.append(tile)
	hand = new_hand
	open_groups.append((tile_list, type_of_match))
	return tile_list, open_groups, hand



[(1,'bamboo'), (1,'bamboo'), (1,'bamboo')]
open_group([(1,'bamboo'), (2,'bamboo'), (3,'bamboo')], 'straight', TILES)



def whichdog(dog):
	print(dog.a)

class Dog:
	def __init__(self):
		self.a = 5
	def wat(self):
		whichdog(self)

orange = Dog()
orange.wat()




from mahjong_ai import Game, Environment, Player

class InteractiveGame:
	def __init__(self, starting_player_idx, my_hand):
		self.env = Environment(TILES, num_players=4)
		self.g = Game(player_list=[Player() for i in range(self.env.num_players)])
		self.g.env.current_player_idx = starting_player_idx
		self.g.player_list[0].hand = my_hand
		for tile in self.g.player_list[0].hand:
			self.env.remaining.pop(self.env.remaining.index(tile))
	def pickup(self, tile):
		self.g.player_list[0].hand.append(tile)
	def discard(self, tile):
		self.env.discard(tile)
		self.g.env.current_player_idx = (self.g.env.current_player_idx + 1) % self.g.env.num_players
		tiles_opened = ig.g.player_list[0].do_pong(self.g, 0)
		if tiles_opened:
			<call pong and open tiles, pick up discarded>
			self.g.env.open_hand(tiles_opened)
			self.g.env.current_player_idx = 0
	def pong(self, player_idx, tile_list):
		self.g.env.current_player_idx = player_idx
		self.g.env.discarded.pop(-1)
		self.g.player_list[self.g.env.current_player_idx].open_groups.append((tile_list, 'flush'))
		self.g.env.open_hand(tile_list)
	def chi(self, tile_list):
		self.g.env.discarded.pop(-1)
		self.g.player_list[self.g.env.current_player_idx].open_groups.append((tile_list, 'straight'))
		self.g.env.open_hand(tile_list)
	def reset_all_players_hands():
		used_tiles = self.g.env.discarded + self.g.player_list[0].hand + [tile for player in self.g.player_list for group in player.open_groups for tile in group[0]]
		possible_remaining_tiles = copy.deepcopy(TILES)
		for tile in used_tiles:
			possible_remaining_tiles.pop(possible_remaining_tiles.index(tile))
		random.shuffle(possible_remaining_tiles)
		for i in range(1,4):
			self.g.player_list[i].hand = possible_remaining_tiles[(i-1)*13:13*i]



<PROMPT: select starting player>
<PROMPT: select my hand>
ig = InteractiveGame(starting_player_idx, my_hand)


<always give option to pong>
ig.pong(player_idx, tile_list)

if ig.g.env.current_player_idx == 0:
	tiles_opened = ig.g.player_list[0].do_chi(self.g)
	if tiles_opened:
		<print call chi open tiles, pick up discarded>
	else:
		<PROMPT: print input tile picked up>
		pickup(tile)
	discard_tile = self.player_list[0].choose_discard(self.g)
	self.env.discard(discard_tile)
	<print discarded tile>
	ig.g.env.current_player_idx = (ig.g.env.current_player_idx + 1) % ig.g.env.num_players
else:
	<give option to click chi, if chi is clicked enter tile list>
	ig.chi(tile_list)
	<PROMPT: enter tile discarded>
	ig.discard(tile)

	


import random
import copy
import numpy as np

from mahjong_ai import *

import cProfile
results = cProfile.run(Game())


g = Game()

hand = [(1,'bamboo')]*3 + \
[(8,'dots')]*3 + \
[(7,'character'), (8,'character'), (9,'character')] + \
[(2,'character'),(6,'character'),(3,'character')] + \
[(2,'bamboo'),(6,'bamboo')]


from mahjong_ai import *
p=Player()

#[(6, 'character'), (-1, 'dong fong'), (7, 'character'), (3, 'bamboo'), (2, 'dots'), (5, 'dots'), (8, 'bamboo'), (2, 'dots'), (9, 'bamboo'), (4, 'bamboo'), (3, 'character'), (1, 'dots'), (5, 'character'), (8, 'dots')]
p.open_groups = [([(6, 'bamboo'), (6, 'bamboo'), (6, 'bamboo')], 'flush'), ([(-1, 'bei fong'), (-1, 'bei fong'), (-1, 'bei fong')], 'flush'), ([(5, 'bamboo'), (5, 'bamboo'), (5, 'bamboo')], 'flush')]

p.hand = [(3, 'dots'), (2, 'dots'), (5, 'dots'), (5, 'dots')]

p.update_winning_tiles()








with open('wat.json', 'w') as f:
	json.dump(g.__dict__, f)

from mahjong_ai import *
p=Player()




p.hand = [(3, 'bamboo'), (4, 'bamboo'), (5, 'bamboo'), (-10, 'bei fong'), (1, 'character'), (1, 'character'), (4, 'dots'), (4, 'dots'), (4, 'dots'), (5, 'dots'), (6, 'dots')]
p.open_groups = [([(5, 'character'), (6, 'character'), (4, 'character')], 'straight')]
p.get_score_on_hand(p.hand)


















p.hand = [(2, 'bamboo'), (2, 'bamboo'), (2, 'bamboo'), (3, 'bamboo'), (4, 'bamboo'), (8, 'bamboo'), (3, 'dots'), (9, 'dots'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(6, 'character'), (8, 'character'), (7, 'character')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(2, 'bamboo'), (2, 'bamboo'), (2, 'bamboo'), (3, 'bamboo'), (4, 'bamboo'), (1, 'dots'), (3, 'dots'), (9, 'dots'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(6, 'character'), (8, 'character'), (7, 'character')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(2, 'bamboo'), (2, 'bamboo'), (2, 'bamboo'), (3, 'bamboo'), (4, 'bamboo'), (3, 'dots'), (9, 'dots'), (-1, 'fa tsi'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(6, 'character'), (8, 'character'), (7, 'character')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(1, 'bamboo'), (2, 'bamboo'), (2, 'bamboo'), (2, 'bamboo'), (3, 'bamboo'), (4, 'bamboo'), (9, 'dots'), (-1, 'fa tsi'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(6, 'character'), (8, 'character'), (7, 'character')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(6, 'bamboo'), (-10, 'dong fong'), (-10, 'dong fong'), (4, 'dots'), (5, 'dots'), (6, 'dots'), (6, 'dots'), (6, 'dots'), (8, 'dots'), (9, 'dots')]
p.open_groups = [([(5, 'character'), (7, 'character'), (6, 'character')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(3, 'bamboo'), (4, 'bamboo'), (4, 'bamboo'), (4, 'bamboo'), (5, 'bamboo'), (-10, 'bei fong'), (5, 'character'), (5, 'character'), (-10, 'dong fong'), (9, 'dots')]
p.open_groups = [([(5, 'dots'), (7, 'dots'), (6, 'dots')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(8, 'bamboo'), (2, 'character'), (7, 'character'), (7, 'character'), (2, 'dots'), (6, 'dots'), (7, 'dots'), (7, 'dots'), (7, 'dots'), (8, 'dots')]
p.open_groups = [([(5, 'bamboo'), (5, 'bamboo'), (5, 'bamboo')], 'flush')]
p.get_score_on_hand(p.hand)

p.hand = [(6, 'bamboo'), (7, 'bamboo'), (2, 'character'), (3, 'character'), (3, 'character'), (3, 'character'), (4, 'character'), (3, 'dots'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(3, 'dots'), (4, 'dots'), (2, 'dots')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(7, 'bamboo'), (2, 'character'), (3, 'character'), (3, 'character'), (3, 'character'), (4, 'character'), (2, 'dots'), (3, 'dots'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(3, 'dots'), (4, 'dots'), (2, 'dots')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(7, 'bamboo'), (2, 'character'), (3, 'character'), (3, 'character'), (3, 'character'), (4, 'character'), (2, 'dots'), (3, 'dots'), (-10, 'hong jong'), (-10, 'hong jong')]
p.open_groups = [([(3, 'dots'), (4, 'dots'), (2, 'dots')], 'straight')]
p.get_score_on_hand(p.hand)

p.hand = [(1, 'character'), (2, 'character'), (2, 'character'), (2, 'character'), (7, 'character'), (7, 'character'), (1, 'dots'), (2, 'dots'), (3, 'dots'), (-10, 'hong jong')]
p.open_groups = [([(8, 'bamboo'), (9, 'bamboo'), (7, 'bamboo')], 'straight')]
p.get_score_on_hand(p.hand)















#p.get_score_on_hand(hand)

hand = [(6,'bamboo'), (7,'bamboo'), (8,'bamboo')] + \
[(6,'character'), (7,'character'), (8,'character')] + \
[(6,'dots'), (7,'dots'), (8,'dots')] + \
[(2,'bamboo'),(2,'bamboo')]


p.open_group([(-1, 'bi liar'),(-1, 'bi liar'),(-1, 'bi liar')], 'flush')
p.get_score_on_hand(hand)




hand2 = [(2,'bamboo')]*2 + [(1,'bamboo'), (3,'bamboo')]

p.get_score_on_hand(hand2)


docker build . -t dustinaxman/mahjong_api

docker run -p 80:80 dustinaxman/mahjong_api

docker push dustinaxman/mahjong_api






from mahjong_ai import Game, Environment, Player, TILES, InteractiveGame



my_hand = [(6,'bamboo'), (7,'bamboo'), (8,'bamboo')] + \
[(6,'character'), (7,'character'), (8,'character')] + \
[(6,'dots'), (7,'dots'), (8,'dots')] + \
[(2,'bamboo'),(2,'bamboo'), (-10, 'bei fong'), (-10, 'bi liar'), (8,'dots')]

starting_player_idx = 0

ig = InteractiveGame(starting_player_idx, my_hand)


discarded_tile = ig.discard(None)

#merge the discard with user discard
#separate so that we can discard for the user and pickup separately for first turn



















from mahjong_ai import Game, Environment, Player, TILES, InteractiveGame


my_hand = [(6,'bamboo'), (7,'bamboo'), (8,'bamboo')] + [(6,'character'), (7,'character'), (8,'character')] + [(6,'dots'), (7,'dots'), (8,'dots')] + [(2,'bamboo'),(2,'bamboo'), (-10, 'bei fong'), (-10, 'bi liar'), (8,'dots')]

starting_player_idx = 0
ig = InteractiveGame(starting_player_idx, my_hand)
discarded_tile = ig.discard(None)
ig.g.env.current_player_idx 
tiles_opened = ig.discard((9,'bamboo'))
tiles_opened
ig.g.env.opened_tiles_per_player
ig.g.env.current_player_idx 
ig.g.env.opened_tiles_per_player
tiles_opened = ig.discard((2,'bamboo'))
tiles_opened
ig.g.env.opened_tiles_per_player
ig.g.env.current_player_idx 
discarded_tile = ig.discard(None)
print("Discard: {}".format(str(discarded_tile)))
ig.g.env.current_player_idx 
ig.chi([(7, 'dots'),(8, 'dots'),(9, 'dots')])
ig.g.player_list[1].open_groups
ig.g.env.opened_tiles_per_player
ig.g.player_list[0].open_groups
ig.g.player_list[1].open_groups
ig.g.player_list[2].open_groups
ig.g.player_list[3].open_groups

tiles_opened = ig.discard((3, 'bamboo'))
ig.g.player_list[0].hand
tiles_opened = ig.discard((8, 'character'))


stop $(docker ps -q) && docker build . -t dustinaxman/mahjong_api && docker run -p 80:80 -e PYTHONUNBUFFERED=1 -d dustinaxman/mahjong_api


import requests
import json

def get_game_state():
    r = requests.get('http://0.0.0.0:80/get-game-state') 
    return r.json()['game_dict']

def start_game(starting_player_idx, my_hand):
    r = requests.post('http://0.0.0.0:80/start-game/{}'.format(starting_player_idx), data={'my_hand': json.dumps(my_hand)}) 
    return r.json()['game_dict']


def pong(pong_player_idx, tile_list):
    r = requests.post('http://0.0.0.0:80/pong/{}'.format(pong_player_idx), data={'tile_list': json.dumps(tile_list)}) 

def get_chi_recommendation():
    r = requests.get('http://0.0.0.0:80/get-chi-recommendation') 
    return r.json()['tiles_opened']

def discard(tile):
    r = requests.post('http://0.0.0.0:80/discard', data={'tile': json.dumps(tile)}) 
    return r.json()['discarded_or_opened']

def chi(tile_list):
    r = requests.post('http://0.0.0.0:80/chi', data={'tile_list': json.dumps(tile_list)}) 

def pickup(tile):
    r = requests.post('http://0.0.0.0:80/pickup', data={'tile': json.dumps(tile)}) 




my_hand = [(6,'bamboo'), (7,'bamboo'), (8,'bamboo')] + [(6,'character'), (7,'character'), (8,'character')] + [(6,'dots'), (7,'dots'), (8,'dots')] + [(2,'bamboo'),(2,'bamboo'), (-10, 'bei fong'), (-10, 'bi liar'), (8,'dots')]
starting_player_idx = 0
game_dict = start_game(starting_player_idx, my_hand)
discarded_tile = discard(None)
game_dict = get_game_state()
game_dict['env']['current_player_idx']
game_dict['env']['discarded']
tiles_opened = discard((9,'bamboo'))
tiles_opened = discard((-10,'bi liar'))
tiles_opened = discard((2,'dots'))
pickup((8, 'dots'))
discarded_tile = discard(None)
print("Discard: {}".format(str(discarded_tile)))
chi([(7, 'dots'),(8, 'dots'),(9, 'dots')])
tiles_opened = discard((3,'bamboo'))
tiles_opened = discard((7,'character'))
tiles_opened = get_chi_recommendation()
print("Call chi, Open tiles: {}, Pick up discarded".format(str(tiles_opened)))
discarded_tile = discard(None)
print("Discard: {}".format(str(discarded_tile)))
pong(3, [discarded_tile, discarded_tile, discarded_tile])


import pathlib
with open(pathlib.Path.home()/'wat.json', 'w') as f:
    json.dump(game_dict, f)


#ALWAYS GIVE THE OPTION
pong(player_idx, tile_list)

#ON MY TURN
if not first_turn:
	tiles_opened = get_chi_recommendation()
	if tiles_opened:
		print("Call chi, Open tiles: {}, Pick up discarded".format(str(tiles_opened)))
	else:
		tile = input("Input tile picked up")
		pickup(tile)
discarded_tile = discard(None)
print("Discard: {}".format(str(discarded_tile)))


#ON OTHERS TURN
<give option to click chi, if chi is clicked enter tile list>
	chi(tile_list)

print("PROMPT: Enter tile discarded")
tiles_opened = discard(tile)
if tiles_opened:
	print("Call pong, pick up discarded, open tiles: {}".format(str(tiles_opened)))
	discarded_tile = discard(None)
	print("Discard: {}".format(str(discarded_tile)))














#make api for following:

game_dict = start_game(starting_player_idx, my_hand)
pong(player_idx, tile_list)
tiles_opened = get_chi_recommendation()
pickup(tile)
chi(tile_list)
discarded_tile = discard(None)
tiles_opened = discard(tile)

#make the api save the state each time as a file

#make the barebokes UI

#run on lambda? serverless?


