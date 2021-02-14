

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
