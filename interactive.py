

from mahjong_ai import Game, Environment, Player, TILES, InteractiveGame



<PROMPT: select starting player>
<PROMPT: select my hand>
my_hand = 
starting_player_idx = 
ig = InteractiveGame(starting_player_idx, my_hand)

<always give option to pong>
ig.pong(player_idx, tile_list)

if ig.g.env.current_player_idx == 0:
	tiles_opened = ig.g.player_list[0].do_chi(self.g)
	if tiles_opened:
		print("Call chi, Open tiles: {}, Pick up discarded".format(str(tiles_opened)))
	else:
		print("PROMPT: Input tile picked up")
		ig.pickup(tile)
	discard_tile = self.player_list[0].choose_discard(self.g)
	self.env.discard(discard_tile)
	print("Discard: {}".format(str(discard_tile)))
	
else:
	<give option to click chi, if chi is clicked enter tile list>
	ig.chi(tile_list)
	print("PROMPT: Enter tile discarded")
	ig.discard(tile)











class InteractiveGame:
    def __init__(self, starting_player_idx=None, my_hand=None, num_players=4, game=None):
        if not game=None:
        	self.g = game
        else:
	        self.g = Game(player_list=[Player() for i in range(num_players)])
	        self.g.env.current_player_idx = starting_player_idx
	        self.g.player_list[0].hand = my_hand
	        for tile in self.g.player_list[0].hand:
	            self.g.env.remaining.pop(self.g.env.remaining.index(tile))
    def pickup(self, tile):
    	if self.g.env.current_player_idx != 0:
    		print('Error: pickup command run for non-user index {}'.format(str(self.g.env.current_player_idx)))
    		return
        self.g.player_list[0].hand.append(tile)
        self.reset_all_players_hands()
    def discard(self, tile):
        current_player_idx = self.g.env.current_player_idx
        if current_player_idx == 0:
        	tile = self.g.player_list[0].discard(self.g)
        self.g.env.discard(tile)
        self.g.env.current_player_idx = (self.g.env.current_player_idx + 1) % self.g.env.num_players
        self.reset_all_players_hands()
    	if not current_player_idx == 0:
	        tiles_opened = self.g.player_list[0].do_pong(self.g, 0)
	        if tiles_opened:
	        	self.g.env.current_player_idx = 0
	            self.g.env.open_hand(tiles_opened)
	            return tiles_opened
	    else:
	    	return tile
    def pong(self, player_idx, tile_list):
        self.g.env.current_player_idx = player_idx
        self.g.env.discarded.pop(-1)
        self.g.player_list[self.g.env.current_player_idx].open_groups.append((tile_list, 'flush'))
        self.g.env.open_hand(tile_list)
        self.g.env.current_player_idx = (self.g.env.current_player_idx + 1) % self.g.env.num_players
        self.reset_all_players_hands()
    def chi(self, tile_list):
        self.g.env.discarded.pop(-1)
        self.g.player_list[self.g.env.current_player_idx].open_groups.append((tile_list, 'straight'))
        self.g.env.open_hand(tile_list)
        self.g.env.current_player_idx = (self.g.env.current_player_idx + 1) % self.g.env.num_players
        self.reset_all_players_hands()
    def get_chi_recommendation(self):
        return self.g.player_list[0].do_chi(self.g)
    def reset_all_players_hands(self):
        used_tiles = self.g.env.discarded + self.g.player_list[0].hand + [tile for player in self.g.player_list for group in player.open_groups for tile in group[0]]
        possible_remaining_tiles = copy.deepcopy(TILES)
        for tile in used_tiles:
            possible_remaining_tiles.pop(possible_remaining_tiles.index(tile))
        random.shuffle(possible_remaining_tiles)
        for i in range(0,4):
            if i != 0:
                num_tiles_to_select = 13 - 3*len(self.g.player_list[i].open_groups)
                self.g.player_list[i].hand = possible_remaining_tiles[0:num_tiles_to_select]
                del possible_remaining_tiles[:num_tiles_to_select]
        self.g.env.remaining = possible_remaining_tiles




from mahjong_ai import Game, Environment, Player, TILES, InteractiveGame


<PROMPT: select starting player>
<PROMPT: select my hand>
my_hand = 
starting_player_idx = 
ig = InteractiveGame(starting_player_idx=starting_player_idx, my_hand=my_hand)

#ALWAYS GIVE THE OPTION
ig.pong(player_idx, tile_list)

#ON MY TURN
if not first_turn:
	tiles_opened = ig.get_chi_recommendation()
	if tiles_opened:
		print("Call chi, Open tiles: {}, Pick up discarded".format(str(tiles_opened)))
	else:
		print("PROMPT: Input tile picked up")
		ig.pickup(tile)
discarded_tile = ig.discard(None)
print("Discard: {}".format(str(discarded_tile)))

#ON OTHERS TURN
<give option to click chi, if chi is clicked enter tile list>
	ig.chi(tile_list)

print("PROMPT: Enter tile discarded")
tiles_opened = ig.discard(tile)
if tiles_opened:
	print("Call pong, pick up discarded, open tiles: {}".format(str(tiles_opened)))
	discarded_tile = ig.discard(None)
	print("Discard: {}".format(str(discarded_tile)))











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





my_hand = ???
starting_player_idx = ???
game_dict = start_game(starting_player_idx, my_hand)

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

