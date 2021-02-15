import random
import copy
import numpy as np

SUITS = ['bamboo', 'dots', 'character']
NUMBERS = range(1, 10)
EXTRA_TILES = [(None, 'fa tsi')]*4 + \
			[(None, 'hong jong')]*4 + \
			[(None, 'bi liar')]*4 + \
			[(None, 'bei fong')]*4 + \
			[(None, 'nan fong')]*4 + \
			[(None, 'dong fong')]*4 + \
			[(None, 'xi fong')]*4
TILES = ([(number, suit) for suit in SUITS for number in NUMBERS] * 4) + EXTRA_TILES
SPECIAL_FLUSH_SCORE_FACTOR = 0.05
NORMAL_FLUSH_SCORE_FACTOR = 0.04
STRAIGHT_SCORE_FACTOR = 0.03
NORMAL_DOUBLE_SCORE_FACTOR = 0.01
SPECIAL_DOUBLE_SCORE_FACTOR = 0.015
MISSING_SUIT_SCORE_PENALTY_FACTOR = 0.06

#TODO:


# test update score
# test game with random play (randomish)
# make sample tree finder

# add in the model or some heuristics for random move selection
# figure out how to get features
# figure out best way to order and present the tiles to model (start with good hands?)
# heuristic based on how many "winning" options there are
# add learning part
# construct fake games meant to teach that you need each suit + 9 1 not 8 and 2

class Environment:
	def __init__(self, tiles, num_players=4):
		self.all_tiles = tiles
		self.discarded = []
		self.num_players = num_players
		self.env.current_player_idx = random.randint(0, self.num_players)
		self.remaining = tiles
		random.shuffle(self.remaining)
		self.opened_tiles_per_player = [[]] * self.num_players
		self.discarded_tiles_per_player = [[]] * self.num_players
	def draw(self, n):
		drawn_tiles = self.remaining[-n:]
		del self.remaining[-n:]
		return drawn_tiles
	def discard(self, tile):
		self.discarded.append(tile)
		self.discarded_tiles_per_player[self.env.current_player_idx].append(tile)
	def open_hand(self, tile_list):
		self.opened_tiles_per_player[self.env.current_player_idx].extend(tile_list)

class Brain:
	def __init__(self):
		self.NUM_PLAYOUTS = 100
		self.REGRESSION_THRESHOLD = -0.035
	def run_playouts(self, game, state):
		if state(2):
			hero_player_idx = state(2)
		else:
			hero_player_idx = game.env.current_player_idx
		total_wins = 0
		for i in range(self.NUM_PLAYOUTS):
			mcts_game = Game(player_list=game.player_list, env=game.env, MCTS=True, state=state)
			mcts_game.play()
			total_wins += 1.0 if mcts_game.player_list[hero_player_idx].score == 1.0 else 0.0
		percentage_wins = total_wins / float(self.NUM_PLAYOUTS)
		return percentage_wins
	def which_chi(self, game, tile_options):
		hero_player_idx = game_option.env.current_player_idx
		options = [None] + tile_options
		option_percentage_wins = []
		if game.MCTS:
			#CHOOSE RANDOM MOVE
			best_option_idx = random.randint(0, len(options))
		else:
			for option in options:
				game_option = copy.deepcopy(game).shuffle_game(hero_player_idx)
				if option == 'None':
					state = ('reject_chi', None, None)
				else:
					game_option.player_list[hero_player_idx].add_to_hand(game_option.env.discarded.pop(-1))
					game_option.player_list[hero_player_idx].open_group(tile_options[i], 'straight')
					state = ('do_chi', tile_options[i], None)
				percentage_wins = self.run_playouts(game_option, state)
				option_percentage_wins.append(percentage_wins)
			best_option_idx = np.argmax(option_percentage_wins)
		return options[best_option_idx]
	def do_pong(self, game, tiles_to_open, pong_player_idx):
		hero_player_idx = pong_player_idx
		options =  [False, True]
		option_percentage_wins = []
		if game.MCTS:
			best_option_idx = random.randint(0, len(options))
		else:
			for option in options:
				game_option = copy.deepcopy(game).shuffle_game(hero_player_idx)
				if option:
					game_option.player_list[hero_player_idx].add_to_hand(game_option.env.discarded.pop(-1))
					game_option.player_list[hero_player_idx].open_group(tiles_to_open, 'flush')
					state = ('do_pong', tiles_to_open, hero_player_idx)
				else:		
					state = ('reject_pong', None, hero_player_idx)
				percentage_wins = self.run_playouts(game_option, state)
				option_percentage_wins.append(percentage_wins)
			best_option_idx = np.argmax(option_percentage_wins)
		return options[best_option_idx]

	def choose_discard(self, game):
		hero_player = game.player_list[game.env.current_player_idx]
		hero_player_idx = game.env.current_player_idx
		options = list(set(hero_player.hand))
		option_percentage_wins = []
		if game.MCTS:
			game_option = copy.deepcopy(game)
			heuristic_filtered_options = []
			for option in options:
				hand_before_removal = game_option.player_list[game_option.env.current_player_idx].hand
				idx_of_option = hand.index(option)
				hand_after_removal = hand[0:idx_of_option] + hand[idx_of_option+1:] + [game_option.env.remaining[-1]]
				score_before_removal = game_option.player_list[game_option.env.current_player_idx].get_score_on_hand(hand_before_removal)
				score_after_removal = game_option.player_list[game_option.env.current_player_idx].get_score_on_hand(hand_after_removal)
				if self.REGRESSION_THRESHOLD < score_after_removal - score_before_removal:
					heuristic_filtered_options.append(option)
			best_option = heuristic_filtered_options(random.randint(0, len(heuristic_filtered_options)))
		else:
			for option in options:
				game_option = copy.deepcopy(game).shuffle_game(hero_player_idx)
				option_card_idx = game_option.player_list[game_option.env.current_player_idx].index(option)
				state = ('after_discard', game_option.player_list[game_option.env.current_player_idx].remove_from_hand(option_card_idx), None)
				percentage_wins = self.run_playouts(game_option, state)
				option_percentage_wins.append(percentage_wins)
			best_option_idx = np.argmax(option_percentage_wins)
			best_option = options[best_option_idx]
		return best_option
				
class Player:
	def __init__(self):
		self.Brain = Brain()
		self.hand = []
		self.open_groups = []
		self.score = 0
		self.winning_tiles = None
	def add_to_hand(self, tile):
		self.hand.append(tile)
	def remove_from_hand(self, tile_index):
		return self.hand.pop(tile_index)
	def check_pong(self, query_tile):
		idxs_of_query_tile_in_hand = [i for i, tile in enumerate(self.hand) if tile == query_tile][:2]
		num_of_query_tile_in_hand = len(idxs_of_query_tile_in_hand)
		return [query_tile, query_tile] if 1 < num_of_query_tile_in_hand else []
	def check_chi(self, query_tile):
		pair_options = [[(query_tile[0]-1, query_tile[1]),(query_tile[0]-2, query_tile[1])], \
						[(query_tile[0]-1, query_tile[1]),(query_tile[0]+1, query_tile[1])], \
						[(query_tile[0]+1, query_tile[1]),(query_tile[0]+2, query_tile[1])]]
		chi_options = []
		chi_index_options = []
		for i in range(3):
			if pair_options[i][0] in self.hand and pair_options[i][1] in self.hand:
				chi_options.append(pair_options[i])
				chi_index_options.append([self.hand.index(pair_options[i][0]), self.hand.index(pair_options[i][1])])
		return chi_options, chi_index_options
	def do_pong(self, root_game, pong_player_idx):
		query_tile = game.env.discarded[-1]
		tiles, idxs = self.check_pong()
		if tiles:
			if self.Brain.do_pong(root_game, tiles + [query_tile], pong_player_idx):
				self.add_to_hand(root_game.env.discarded.pop(-1))
				self.open_group(tiles + [query_tile], 'flush')
				return tiles + [query_tile]
		return None
	def do_chi(self, root_game):
		query_tile = game.env.discarded[-1]
		tile_options, idxs = self.check_chi()
		if tile_options:
			tiles = self.Brain.which_chi(root_game, [option + [query_tile] for option in tile_options])
			if tiles:
				self.add_to_hand(root_game.env.discarded.pop(-1))
				self.open_group(tiles, 'straight')
				return tiles
		return None
	def open_group(self, tile_list, type_of_match):
		tile_set = set(tile_list)
		count = 0
		new_hand = []
		for tile in self.hand:
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
		self.hand = new_hand
		self.open_groups.append((tile_list, type_of_match))
		return tile_list
	def discard(self, game):
		discard_idx = self.Brain.choose_discard(game)
		return self.remove_from_hand(discard_idx)


	def get_score_on_hand(self, hand):
		score = 0
		self.open_suit_list = []
		straight_count_open = 0
		special_flush_count_open = 0
		normal_flush_count_open = 0
		if self.open_groups:
			score = 0.1
			special_flush_count_open = len([group for group in self.open_groups if group[0][0][1] not in SUITS])
			normal_flush_count_open = len([group for group in self.open_groups if group[0][0][1] in SUITS and group[1] == 'flush'])
			straight_count_open = len([group for group in self.open_groups if group[1] == 'straight'])
			score += special_flush_count_open * SPECIAL_FLUSH_SCORE_FACTOR
			score += normal_flush_count_open * NORMAL_FLUSH_SCORE_FACTOR
			score += straight_count_open * STRAIGHT_SCORE_FACTOR
			self.open_suit_list = [group[0][0][1] for group in self.open_groups]
			num_suits_unopened = len([suit for suit in SUITS if suit not in self.open_suit_list])
			if num_suits_unopened-1 > (4 - len(self.open_groups)):
				score = 0
				return score
		hand = sorted(hand, key=lambda tile: [tile[1], tile[0]])
		print(hand)
		suits_counted_towards_score = self.open_suit_list
		used_tile_idxs = []
		special_flush_count = 0
		normal_flush_count = 0
		straight_count = 0
		no_straight_flag = False
		no_flush_flag = False
		last_tile = None
		straight_tracker = 0
		flush_tracker = 0
		used_tile_candidate_list_flush = []
		used_tile_candidate_list_straight = []
		for i, tile in enumerate(hand):
			if last_tile == (tile[0] - 1, tile[1]):
				used_tile_candidate_list_straight.append(i)
				print('straight')
				print(tile)
				print(i)
				flush_tracker = 0
				if not no_straight_flag:
					if straight_tracker < 1:
						straight_tracker += 1
					else:
						used_tile_idxs.extend(used_tile_candidate_list_straight)
						used_tile_candidate_list_straight = []
						straight_count += 1
						no_straight_flag = True
						suits_counted_towards_score.append(tile[1])
				else:
					no_straight_flag = False
			elif last_tile == tile:
				print('flush')
				print(tile)
				print(i)
				used_tile_candidate_list_flush.extend([i-1, i])
				if not no_flush_flag:
					print(flush_tracker)
					if flush_tracker < 1:
						flush_tracker += 1
					else:
						used_tile_idxs.extend(used_tile_candidate_list_flush)
						used_tile_candidate_list_flush = []
						if tile[1] in SUITS:
							normal_flush_count += 1
						else:
							special_flush_count += 1
						suits_counted_towards_score.append(tile[1])
						no_flush_flag = True
				else:
					no_flush_flag = False
			else:
				used_tile_candidate_list_flush = []
				used_tile_candidate_list_straight = []
				flush_tracker = 0
				straight_tracker = 0
				no_straight_flag = False
				no_flush_flag = False
				if flush_tracker == 0:
					used_tile_candidate_list_flush.append(i)
				if straight_tracker == 0:
					used_tile_candidate_list_straight.append(i)
			last_tile = tile
		flush_tracker = 0
		no_flush_flag = False
		special_double_count = 0
		normal_double_count = 0
		doubles_list = []
		last_tile = None
		print(used_tile_idxs)
		for i, tile in enumerate(hand):
			if i not in used_tile_idxs:
				if last_tile == tile and tile[0] not in [2, 8]:
					if tile[1] in SUITS:
						normal_double_count += 1
					else:
						special_double_count += 1
					used_tile_idxs.extend([i-1, i])
					doubles_list.append([hand[i-1], hand[i]])
					suits_counted_towards_score.append(tile[1])
				else:
					flush_tracker = 0
				last_tile = tile

		score += special_flush_count * SPECIAL_FLUSH_SCORE_FACTOR
		score += normal_flush_count * NORMAL_FLUSH_SCORE_FACTOR
		score += straight_count * STRAIGHT_SCORE_FACTOR
		score += normal_double_count * NORMAL_DOUBLE_SCORE_FACTOR
		score += special_double_count * SPECIAL_DOUBLE_SCORE_FACTOR

		missing_suits = [suit for suit in SUITS if suit not in suits_counted_towards_score]
		missing_suits_score_penalty = max(len(suits_counted_towards_score) + len(missing_suits) - 5, 0) * MISSING_SUIT_SCORE_PENALTY_FACTOR
		score -= missing_suits_score_penalty

		num_groups = (special_flush_count + normal_flush_count + straight_count + straight_count_open + special_flush_count_open + normal_flush_count_open)
		four_groups = num_groups == 4
		num_doubles = normal_double_count + special_double_count
		one_double = num_doubles == 1
		all_suits = len(missing_suits) == 0
		at_least_one_special_group = (special_double_count > 0 or special_flush_count > 0 or special_flush_count_open > 0)
		at_least_one_flush = normal_flush_count + normal_flush_count_open > 0
		cards_in_open_groups = [tile for group in self.open_groups for tile in group[0]]
		all_tiles_for_player = hand + cards_in_open_groups
		one_or_nine_in_hand = any([tile[0] in [1, 9] for tile in all_tiles_for_player])
		if one_or_nine_in_hand:
			score += 0.005
		win = four_groups \
			and one_double \
			and all_suits \
			and self.open_groups \
			and (at_least_one_special_group \
			or (at_least_one_flush and one_or_nine_in_hand))
		if win:
			score = 1.0
		dict_of_values_for_remaining_tile_calculation = {}
		dict_of_values_for_remaining_tile_calculation['used_tile_idxs'] = used_tile_idxs
		dict_of_values_for_remaining_tile_calculation['num_doubles'] = num_doubles
		dict_of_values_for_remaining_tile_calculation['num_groups'] = num_groups 
		dict_of_values_for_remaining_tile_calculation['doubles_list'] = doubles_list
		dict_of_values_for_remaining_tile_calculation['one_or_nine_in_hand'] = one_or_nine_in_hand
		dict_of_values_for_remaining_tile_calculation['at_least_one_special_group'] = at_least_one_special_group
		dict_of_values_for_remaining_tile_calculation['at_least_one_flush'] = at_least_one_flush
		dict_of_values_for_remaining_tile_calculation['doubles_list'] = doubles_list
		return score, dict_of_values_for_remaining_tile_calculation

	def update_score(self):
		self.score, _ = self.get_score_on_hand(self.hand)

	def get_missing_of_straight(self, tiles):
		number_diff = tiles[1][0] - tiles[0][0]
		if number_diff == 1:
			return [[tiles[1][0]+1, tiles[1][1]], [tiles[1][0]-2, tiles[1][1]]]
		elif number_diff == 2:
			return [[tiles[1][0]-1, tiles[1][1]]]
		else:
			raise ValueError('No straight found with tiles: {}'.format(' and '.join(tiles)))

	def update_winning_tiles(self):
		self.winning_tiles = None
		score, dict_of_values_for_remaining_tile_calculation = self.get_score_on_hand(self.hand)

		used_tile_idxs = dict_of_values_for_remaining_tile_calculation['used_tile_idxs']
		num_doubles = dict_of_values_for_remaining_tile_calculation['num_doubles']
		num_groups = dict_of_values_for_remaining_tile_calculation['num_groups']
		doubles_list = dict_of_values_for_remaining_tile_calculation['doubles_list']
		one_or_nine_in_hand = dict_of_values_for_remaining_tile_calculation['one_or_nine_in_hand']
		at_least_one_special_group = dict_of_values_for_remaining_tile_calculation['at_least_one_special_group']
		at_least_one_flush = dict_of_values_for_remaining_tile_calculation['at_least_one_flush']
		doubles_list = dict_of_values_for_remaining_tile_calculation['doubles_list']

		leftover_tiles = [tile for i, tile in enumerate(self.hand) if tile not in used_tile_idxs]
		if len(missing_suits) <= 1 and num_groups >= 3:
			if num_doubles == 2:
				if len(missing_suits) == 0 and (at_least_one_special_group or one_or_nine_in_hand):
					self.winning_tiles = [double[0] for double in doubles_list]
			elif num_doubles == 1:
				if leftover_tiles[0][0] - leftover_tiles[1][0] >= -2 and leftover_tiles[0][0] - leftover_tiles[1][0] <= 2 and leftover_tiles[0][1] == leftover_tiles[1][1]:
					candidate_tiles = self.get_missing_of_straight(leftover_tiles)
					if at_least_one_special_group:
						self.winning_tiles = candidate_tiles
					elif at_least_one_flush:
						if one_or_nine_in_hand:
							self.winning_tiles = candidate_tiles
						else:
							self.winning_tiles = [tile for tile in candidate_tiles if tile[0] in [1, 9]]
			elif num_groups == 4:
				if ((one_or_nine_in_hand and at_least_one_flush) or at_least_one_special_group) and (leftover_tiles[0][0] not in [2, 8]) and (len(missing_suits) == 0 or missing_suits[0] == leftover_tiles[0][1]):
					self.winning_tiles == [tile for i, tile in enumerate(hand) if tile not in used_tile_idxs]
		return self.winning_tiles

		
class Game:
	def __init__(self, player_list=None, env=None, MCTS=False, state=('start', None, None)):
		self.MCTS = MCTS
		self.env = env if env else Environment(TILES, num_players=4)
		self.game_end = False
		if player_list:
			self.player_list = player_list
		else:
			self.player_list = [Player() for i in range(self.env.num_players)]
			for player in self.player_list:
				for tile in self.env.draw(13):
					player.add_to_hand(tile)
			self.current_player_draw()
			self.env.discard(self.player_list[self.env.current_player_idx].discard(self.env))
		if state[0] != 'start':
			self.set_state(state)

	def shuffle_game(self, hero_player_idx):
		used_tiles = self.env.discarded + self.player_list[hero_player_idx].hand + [tile for player in self.player_list for group in player.open_groups for tile in group[0]]
		possible_remaining_tiles = copy.deepcopy(self.env.all_tiles)
		for tile in used_tiles:
			possible_remaining_tiles.pop(possible_remaining_tiles.index(tile))
		random.shuffle(possible_remaining_tiles)
		for i in range(0,4):
			if i != hero_player_idx:
				self.player_list[i].hand = possible_remaining_tiles[(i-1)*13:13*i]
		self.env.discarded = possible_remaining_tiles[4*13:]

	def set_state(state):
		if state[0] == 'do_pong':
			tiles_opened = state[1]
			self.env.current_player_idx = state[2]
			self.env.open_hand(tiles_opened)
			self.player_list[self.env.current_player_idx].update_score()
			if not self.player_list[self.env.current_player_idx].score < 1:
				self.game_end = True
				return
			self.env.discard(self.player_list[self.env.current_player_idx].choose_discard(self))
			self.player_list[self.env.current_player_idx].update_winning_tiles()		
			for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
				if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
					self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
					self.player_list[i % self.num_players].update_score()
					self.game_end = True
					return
		elif state[0] == 'reject_pong':
			if state[2] + 1 > self.env.current_player_idx:
				i = state[2] + 1
			else:
				i = state[2] + 1 + self.num_players
			while i < self.env.current_player_idx + self.num_players:
				tiles_opened = self.player_list[i % self.env.num_players].do_pong(self, i % self.env.num_players)
				if tiles_opened:
					self.env.current_player_idx = i
					self.env.open_hand(tiles_opened)
					self.game_end = True
					return
				i += 1
			else:
				tiles_opened = self.player_list[self.env.current_player_idx].do_chi(self)
				if tiles_opened:
					self.env.open_hand(tiles_opened)
				else:
					if len(self.env.remaining) == 0:
						self.game_end = True
						return
					else:
						self.current_player_draw()
			self.player_list[self.env.current_player_idx].update_score()
			if not self.player_list[self.env.current_player_idx].score < 1:
				return
			self.env.discard(self.player_list[self.env.current_player_idx].choose_discard(self))
			self.player_list[self.env.current_player_idx].update_winning_tiles()		
			for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
				if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
					self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
					self.player_list[i % self.num_players].update_score()
					self.game_end = True
					return

		elif state[0] == 'do_chi':
			self.env.open_hand(state[1])
			self.player_list[self.env.current_player_idx].update_score()
			if not self.player_list[self.env.current_player_idx].score < 1:
				self.game_end = True
				return
			self.env.discard(self.player_list[self.env.current_player_idx].choose_discard(self))
			self.player_list[self.env.current_player_idx].update_winning_tiles()		
			for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
				if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
					self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
					self.player_list[i % self.num_players].update_score()
					self.game_end = True
					return
		elif state[0] == 'reject_chi':
			if len(self.env.remaining) == 0:
				self.game_end = True
				return
			else:
				self.current_player_draw()
			self.player_list[self.env.current_player_idx].update_score()
			if not self.player_list[self.env.current_player_idx].score < 1:
				self.game_end = True
				return
			self.env.discard(self.player_list[self.env.current_player_idx].choose_discard(self))
			self.player_list[self.env.current_player_idx].update_winning_tiles()		
			for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
				if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
					self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
					self.player_list[i % self.num_players].update_score()
					self.game_end = True
					return
		elif state[0] == 'after_discard':
			discard_tile = state[1]
			self.env.discard(discard_tile)
			self.player_list[self.env.current_player_idx].update_winning_tiles()		
			for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
				if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
					self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
					self.player_list[i % self.num_players].update_score()
					self.game_end = True
					return
		
	def current_player_draw(self):
		self.player_list[self.env.current_player_idx].add_to_hand(self.env.draw(1)[0])

	def play_turn(self):
		self.env.current_player_idx = (self.env.current_player_idx + 1) % self.env.num_players
		i = self.env.current_player_idx
		while i < self.env.current_player_idx + self.num_players:
			tiles_opened = self.player_list[i % self.env.num_players].do_pong(self, i % self.env.num_players)
			if tiles_opened:
				self.env.current_player_idx = i
				self.env.open_hand(tiles_opened)
				break
			i += 1
		else:
			tiles_opened = self.player_list[self.env.current_player_idx].do_chi(self)
			if tiles_opened:
				self.env.open_hand(tiles_opened)
			else:
				if len(self.env.remaining) == 0:
					self.game_end = True
					return
				else:
					self.current_player_draw()
		self.player_list[self.env.current_player_idx].update_score()
		if not self.player_list[self.env.current_player_idx].score < 1:
			self.game_end = True
			return
		discard_tile = self.player_list[self.env.current_player_idx].choose_discard(self)
		self.env.discard(discard_tile)
		self.player_list[self.env.current_player_idx].update_winning_tiles()		
		for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
			if self.env.discarded[-1] in self.player_list[i % self.num_players].winning_cards:
				self.player_list[i % self.num_players].add_to_hand(self.env.discarded.pop(-1))
				self.player_list[i % self.num_players].update_score()
				self.game_end = True
				return
	def play():
		while not self.game_end:
			self.play_turn()










