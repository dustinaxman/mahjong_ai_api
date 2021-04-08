

from mahjong_ai import Game, Environment, Player, TILES

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
			print("Call pong, pick up discarded, open tiles: {}".format(str(tiles_opened)))
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
		for i in range(0,4):
			if i != 0:
				num_tiles_to_select = 13 - 3*len(self.player_list[i].open_groups)
				self.player_list[i].hand = possible_remaining_tiles[0:num_tiles_to_select]
				del possible_remaining_tiles[:num_tiles_to_select]
		self.g.env.remaining = possible_remaining_tiles



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








<PROMPT: select starting player>
<PROMPT: select my hand>
my_hand = 
starting_player_idx = 
ig = InteractiveGame(starting_player_idx, my_hand)


#ALWAYS GIVE THE OPTION
ig.pong(player_idx, tile_list)


#ON MY TURN
tiles_opened = ig.g.player_list[0].do_chi(self.g)
if tiles_opened:
	print("Call chi, Open tiles: {}, Pick up discarded".format(str(tiles_opened)))
else:
	print("PROMPT: Input tile picked up")
	ig.pickup(tile)
discard_tile = self.player_list[0].choose_discard(self.g)
self.env.discard(discard_tile)
print("Discard: {}".format(str(discard_tile)))


#ON OTHERS TURN
<give option to click chi, if chi is clicked enter tile list>
ig.chi(tile_list)
print("PROMPT: Enter tile discarded")
ig.discard(tile)










