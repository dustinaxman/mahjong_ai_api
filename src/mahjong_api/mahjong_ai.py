import random
import copy
import numpy as np
from collections import defaultdict
import time
from multiprocessing import Process, Pipe
import json


SUITS = ['bamboo', 'dots', 'character']
NUMBERS = range(1, 10)
EXTRA_TILES = [(-10, 'fa tsi')]*4 + \
            [(-10, 'hong jong')]*4 + \
            [(-10, 'bi liar')]*4 + \
            [(-10, 'bei fong')]*4 + \
            [(-10, 'nan fong')]*4 + \
            [(-10, 'dong fong')]*4 + \
            [(-10, 'xi fong')]*4
TILES = ([(number, suit) for suit in SUITS for number in NUMBERS] * 4) + EXTRA_TILES
SPECIAL_FLUSH_SCORE_FACTOR = 0.1
NORMAL_FLUSH_SCORE_FACTOR = 0.08
STRAIGHT_SCORE_FACTOR = 0.07
NORMAL_DOUBLE_SCORE_FACTOR = 0.03
SPECIAL_DOUBLE_SCORE_FACTOR = 0.05
MISSING_SUIT_SCORE_PENALTY_FACTOR = 0.04
ONE_OR_NINE_SCORE_FACTOR = 0.02

#TODO:


#put in lambda
#make the bi liar and others stronger!!

# figure out how to get features
# figure out best way to order and present the tiles to model (start with good hands?)
# add in the model or some heuristics for random move selection

# add learning part
# construct fake games meant to teach that you need each suit + 9 1 not 8 and 2


def spawn(f):
    def fun(pipe, x):
        pipe.send(f(x))
        pipe.close()
    return fun

def parmap(f, X):
    pipe = [Pipe() for x in X]
    proc = [Process(target=spawn(f), args=(c, x)) for x, (p, c) in zip(X, pipe)]
    [p.start() for p in proc]
    [p.join() for p in proc]
    return [p.recv() for (p, c) in pipe]


class Environment:
    def __init__(self, tiles, num_players=4, seed=None):
        self.discarded = []
        self.num_players = num_players
        random.seed(seed)
        self.current_player_idx = random.randint(0, self.num_players-1)
        self.remaining = tiles
        random.seed(seed)
        random.shuffle(self.remaining)
        self.opened_tiles_per_player = [[] for _ in range(self.num_players)]
        self.discarded_tiles_per_player = [[] for _ in range(self.num_players)]
    def to_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump(self.__dict__, f)
    def from_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            self.__dict__ = json.load(f)
        self.__dict__['discarded'] = [tuple(tile) for tile in self.__dict__['discarded']]
        self.__dict__['remaining'] = [tuple(tile) for tile in self.__dict__['remaining']]
        self.__dict__['opened_tiles_per_player'] = [[tuple(tile) for tile in player_tiles] for player_tiles in self.__dict__['opened_tiles_per_player']]
        self.__dict__['discarded_tiles_per_player'] = [[tuple(tile) for tile in player_tiles] for player_tiles in self.__dict__['discarded_tiles_per_player']]
    def draw(self, n):
        drawn_tiles = self.remaining[-n:]
        del self.remaining[-n:]
        return drawn_tiles
    def discard(self, tile):
        self.discarded.append(tile)
        self.discarded_tiles_per_player[self.current_player_idx].append(tile)
    def open_hand(self, tile_list):
        self.opened_tiles_per_player[self.current_player_idx].extend(tile_list)

class Brain:
    def __init__(self):
        self.NUM_PLAYOUTS = 100
        self.REGRESSION_THRESHOLD = -0.02
    def to_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump(self.__dict__, f)
    def from_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            self.__dict__ = json.load(f)
    def run_playouts(self, game, state):
        if state[2] is not None:
            hero_player_idx = state[2]
        else:
            hero_player_idx = game.env.current_player_idx
        total_wins = 0
        for i in range(self.NUM_PLAYOUTS):
            game.shuffle_game(hero_player_idx)
            if game.RANDSEED is not None:
                mcts_game = Game(player_list=copy.deepcopy(game.player_list), env=copy.deepcopy(game.env), MCTS=True, state=state, RANDSEED=game.RANDSEED+1)
            else:
                mcts_game = Game(player_list=copy.deepcopy(game.player_list), env=copy.deepcopy(game.env), MCTS=True, state=state)
            mcts_game.play(num_turns_to_run=12)
            total_wins += mcts_game.player_list[hero_player_idx].score
            #total_wins += 1.0 if mcts_game.player_list[hero_player_idx].score == 1.0 else 0.0
        percentage_wins = total_wins / float(self.NUM_PLAYOUTS)
        return percentage_wins
    def which_chi(self, game, tile_options):
        hero_player_idx = game.env.current_player_idx
        options = [None] + tile_options
        option_percentage_wins = []
        if game.MCTS:
            #CHOOSE RANDOM MOVE
            random.seed(game.RANDSEED)
            best_option_idx = random.randint(0, len(options)-1)
            if game.RANDSEED is not None:
                game.RANDSEED += 1
        else:
            for option in options:
                game_option = copy.deepcopy(game)
                game_option.shuffle_game(hero_player_idx)
                if option is None:
                    state = ('reject_chi', None, None)
                else:
                    game_option.player_list[hero_player_idx].add_to_hand(game_option.env.discarded.pop(-1))
                    game_option.player_list[hero_player_idx].open_group(option, 'straight')
                    state = ('do_chi', option, None)
                percentage_wins = self.run_playouts(game_option, state)
                option_percentage_wins.append(percentage_wins)
            best_option_idx = np.argmax(option_percentage_wins)
        return options[best_option_idx]
    def do_pong(self, game, tiles_to_open, pong_player_idx):
        hero_player_idx = pong_player_idx
        options =  [False, True]
        option_percentage_wins = []
        if game.MCTS:
            random.seed(game.RANDSEED)
            best_option_idx = random.randint(0, len(options)-1)
            if game.RANDSEED is not None:
                game.RANDSEED += 1
        else:
            for option in options:
                game_option = copy.deepcopy(game)
                game_option.shuffle_game(hero_player_idx)
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
            ##game_option = copy.deepcopy(game)
            # heuristic_filtered_options = []
            # for option in options:
            #   hand_before_removal = game.player_list[game.env.current_player_idx].hand
            #   idx_of_option = hand_before_removal.index(option)
            #   if not len(game.env.remaining) == 0:
            #       hand_after_removal = hand_before_removal[0:idx_of_option] + hand_before_removal[idx_of_option+1:] + [game.env.remaining[-1]]
            #       score_before_removal = game.player_list[game.env.current_player_idx].get_score_on_hand(hand_before_removal)[0]
            #       score_after_removal = game.player_list[game.env.current_player_idx].get_score_on_hand(hand_after_removal)[0]
            #       if self.REGRESSION_THRESHOLD < score_after_removal - score_before_removal:
            #           heuristic_filtered_options.append(option)
            #   else:
            #       heuristic_filtered_options.append(option)
            # if len(heuristic_filtered_options) != 0:
            # best_option = heuristic_filtered_options[random.randint(0, len(heuristic_filtered_options)-1)]
            # else:
            #best_option = options[random.randint(0, len(options)-1)] #TODO replace with self.get_action_eval
            random.seed(game.RANDSEED)
            best_option = options[random.randint(0, len(options)-1)]
            if game.RANDSEED is not None:
                game.RANDSEED += 1
        else:
            print('********************')
            print('********************')
            print('********************')
            print('PLAYER:' + str(hero_player_idx))
            print(game.player_list[hero_player_idx].score)
            print('********************')
            print(hero_player.open_groups)
            print('********************')
            used_tiles = game.env.discarded + game.player_list[hero_player_idx].hand + [tile for player in game.player_list for group in player.open_groups for tile in group[0]]
            possible_remaining_tiles = copy.deepcopy(TILES)
            for tile in used_tiles:
                possible_remaining_tiles.pop(possible_remaining_tiles.index(tile))
            tile_count = defaultdict(int)
            for tile in possible_remaining_tiles:
                tile_count[tile] += 1
            for tile, count in sorted(tile_count.items(), key=lambda tile_count: [tile_count[0][1], tile_count[0][0]]):
                print(str(tile) + " : " + str(count))
            print('############')
            start = time.time()
            # for option in options:
            #     option_percentage_wins.append(self.run_discard_option((option, game)))
            option_percentage_wins = parmap(self.run_discard_option, list(zip(options, [game for i in range(len(options))])))
            best_option_idx = np.argmax(option_percentage_wins)
            best_option = options[best_option_idx]
            tmp_map = {}
            for option_tmp, score_avg in zip(options, option_percentage_wins):
                tmp_map[option_tmp] = "{:.3f}".format(score_avg)
            for option_tmp in sorted(hero_player.hand, key=lambda tile: [tile[1], tile[0]]):
                print(str(option_tmp) + ": " + tmp_map[option_tmp])
            print('############')
            print(best_option)
            print('############')
            print(time.time() - start)
            print('********************')
        return best_option
    def run_discard_option(self, option_game):
        option, game = option_game
        game_option = copy.deepcopy(game)
        option_card_idx = game_option.player_list[game_option.env.current_player_idx].hand.index(option)
        state = ('after_discard', game_option.player_list[game_option.env.current_player_idx].remove_from_hand(option_card_idx), None)
        playout_heuristic = self.run_playouts(game_option, state)
        return playout_heuristic


                
class Player:
    def __init__(self):
        self.Brain = Brain()
        self.hand = []
        self.open_groups = []
        self.score = 0
        self.winning_tiles = []
    def to_dict(self):
        json_out = copy.deepcopy(self.__dict__)
        json_out['Brain'] = self.Brain.__dict__
        return json_out
    def to_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump(self.to_dict(), f)
    def from_json(self, json_file_path):
        with open(json_file_path, 'r') as f:
            tmp_player_dict = json.load(f)
        tmp_player_dict["hand"] = [tuple(tile) for tile in tmp_player_dict["hand"]]
        tmp_player_dict["open_groups"] = [([tuple(tile) for tile in open_group[0]], open_group[1]) for open_group in tmp_player_dict["open_groups"]]
        self.from_dict(tmp_player_dict)
    def from_dict(self, dict_to_load):
        b = self.Brain
        self.__dict__ = dict_to_load
        b.__dict__ = self.__dict__['Brain']
        self.Brain = b
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
        query_tile = root_game.env.discarded[-1]
        tiles = self.check_pong(query_tile)
        if tiles:
            if self.Brain.do_pong(root_game, tiles + [query_tile], pong_player_idx):
                self.add_to_hand(root_game.env.discarded.pop(-1))
                self.open_group(tiles + [query_tile], 'flush')
                return tiles + [query_tile]
        return None
    def do_chi(self, root_game):
        query_tile = root_game.env.discarded[-1]
        tile_options, idxs = self.check_chi(query_tile)
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
        discard_tile = self.Brain.choose_discard(game)
        return self.remove_from_hand(self.hand.index(discard_tile))


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
            self.open_suit_list = [group[0][0][1] for group in self.open_groups]
            num_suits_unopened = len([suit for suit in SUITS if suit not in self.open_suit_list])
            if num_suits_unopened-1 > (4 - len(self.open_groups)):
                dict_of_values_for_remaining_tile_calculation = {}
                dict_of_values_for_remaining_tile_calculation['used_tile_idxs'] = []
                dict_of_values_for_remaining_tile_calculation['num_doubles'] = 0
                dict_of_values_for_remaining_tile_calculation['num_groups'] = 0 
                dict_of_values_for_remaining_tile_calculation['doubles_list'] = []
                dict_of_values_for_remaining_tile_calculation['one_or_nine_in_hand'] = False
                dict_of_values_for_remaining_tile_calculation['at_least_one_special_group'] = False
                dict_of_values_for_remaining_tile_calculation['at_least_one_flush'] = False
                dict_of_values_for_remaining_tile_calculation['doubles_list'] = False
                dict_of_values_for_remaining_tile_calculation['missing_suits'] = []
                dict_of_values_for_remaining_tile_calculation['leftover_tiles'] = []
                dict_of_values_for_remaining_tile_calculation['overlapping_tiles_used'] = True
                score = 0
                return score, dict_of_values_for_remaining_tile_calculation
        hand = sorted(hand, key=lambda tile: [tile[1], tile[0]])
        suits_counted_towards_score = self.open_suit_list
        used_tile_idxs = []
        special_flush_count = 0
        normal_flush_count = 0
        straight_count = 0

        tile_to_index_list_map = defaultdict(list)
        for i, tile in enumerate(hand):
            tile_to_index_list_map[tile].append(i)
            if len(tile_to_index_list_map[tile]) == 3:
                flush_tile_idxs = tile_to_index_list_map[tile]
                used_tile_idxs.extend(flush_tile_idxs)
                flush_suit = hand[flush_tile_idxs[0]][1]
                if flush_suit in SUITS:
                    normal_flush_count += 1
                else:
                    special_flush_count += 1
                suits_counted_towards_score.append(flush_suit)
                tile_to_index_list_map[tile] = []

        no_straight_flag = False
        last_tile = None
        straight_tracker = 0
        used_tile_candidate_list_straight = []
        for i, tile in enumerate(hand):
            if i not in used_tile_idxs:
                if last_tile == (tile[0] - 1, tile[1]):
                    used_tile_candidate_list_straight.append(i)
                    if not no_straight_flag:
                        if straight_tracker < 1:
                            straight_tracker += 1
                        else:
                            used_tile_idxs.extend(used_tile_candidate_list_straight)
                            used_tile_candidate_list_straight = []
                            straight_count += 1
                            no_straight_flag = True
                            straight_tracker = 0
                            suits_counted_towards_score.append(tile[1])
                    else:
                        no_straight_flag = False
                elif tile == last_tile:
                    no_straight_flag = False
                else:
                    used_tile_candidate_list_straight = []
                    straight_tracker = 0
                    no_straight_flag = False
                    if straight_tracker == 0:
                        used_tile_candidate_list_straight.append(i)
                last_tile = tile

        special_double_count = 0
        normal_double_count = 0
        doubles_list = []
        last_tile = None
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
                last_tile = tile

        missing_suits = [suit for suit in SUITS if suit not in suits_counted_towards_score]
        num_groups = (special_flush_count + normal_flush_count + straight_count + straight_count_open + special_flush_count_open + normal_flush_count_open)
        four_groups = num_groups == 4
        num_doubles = normal_double_count + special_double_count
        one_double = num_doubles == 1
        all_suits = len(missing_suits) == 0
        at_least_one_special_group = (special_double_count > 0 or special_flush_count > 0 or special_flush_count_open > 0)
        at_least_one_flush = normal_flush_count + normal_flush_count_open > 0
        tiles_in_open_groups = [tile for group in self.open_groups for tile in group[0]]
        all_tiles_for_player = hand + tiles_in_open_groups
        one_or_nine_in_hand = any([tile[0] in [1, 9] for tile in all_tiles_for_player])
        leftover_tiles = [tile for i, tile in enumerate(hand) if i not in used_tile_idxs]
        overlapping_tiles_used = (len(leftover_tiles) + 3*num_groups + 2*num_doubles) > len(hand) + 3*len(self.open_groups)
        
        score += one_or_nine_in_hand * ONE_OR_NINE_SCORE_FACTOR
        score += special_flush_count * SPECIAL_FLUSH_SCORE_FACTOR
        score += normal_flush_count * NORMAL_FLUSH_SCORE_FACTOR
        score += straight_count * STRAIGHT_SCORE_FACTOR
        score += normal_double_count * NORMAL_DOUBLE_SCORE_FACTOR
        score += special_double_count * SPECIAL_DOUBLE_SCORE_FACTOR
        score += special_flush_count_open * SPECIAL_FLUSH_SCORE_FACTOR
        score += normal_flush_count_open * NORMAL_FLUSH_SCORE_FACTOR
        score += straight_count_open * STRAIGHT_SCORE_FACTOR
        score -= len(missing_suits) * MISSING_SUIT_SCORE_PENALTY_FACTOR

        win = four_groups \
            and not overlapping_tiles_used \
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
        dict_of_values_for_remaining_tile_calculation['missing_suits'] = missing_suits
        dict_of_values_for_remaining_tile_calculation['leftover_tiles'] = leftover_tiles
        dict_of_values_for_remaining_tile_calculation['overlapping_tiles_used'] = overlapping_tiles_used
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
            raise ValueError('No straight found with tiles: {}'.format(' and '.join([str(tile[0])+"|"+tile[1] for tile in tiles])))

    def update_winning_tiles(self):
        self.hand = sorted(self.hand, key=lambda tile: [tile[1], tile[0]])
        self.winning_tiles = []
        score, dict_of_values_for_remaining_tile_calculation = self.get_score_on_hand(self.hand)

        used_tile_idxs = dict_of_values_for_remaining_tile_calculation['used_tile_idxs']
        num_doubles = dict_of_values_for_remaining_tile_calculation['num_doubles']
        num_groups = dict_of_values_for_remaining_tile_calculation['num_groups']
        doubles_list = dict_of_values_for_remaining_tile_calculation['doubles_list']
        one_or_nine_in_hand = dict_of_values_for_remaining_tile_calculation['one_or_nine_in_hand']
        at_least_one_special_group = dict_of_values_for_remaining_tile_calculation['at_least_one_special_group']
        at_least_one_flush = dict_of_values_for_remaining_tile_calculation['at_least_one_flush']
        doubles_list = dict_of_values_for_remaining_tile_calculation['doubles_list']
        missing_suits = dict_of_values_for_remaining_tile_calculation['missing_suits']
        leftover_tiles = dict_of_values_for_remaining_tile_calculation['leftover_tiles']
        overlapping_tiles_used = dict_of_values_for_remaining_tile_calculation['overlapping_tiles_used']

        if overlapping_tiles_used:
            #here we have overlapping tiles on purpose since we have straight or flush depending on which tile we use for what here we cannot win with overlap
            self.winning_tiles = []
            return self.winning_tiles
        if len(missing_suits) <= 1 and num_groups >= 3:
            if num_doubles == 2:
                #remaining is 2 doubles (neither is 2 or 8)
                if len(missing_suits) == 0:
                    if (at_least_one_special_group or one_or_nine_in_hand):
                        self.winning_tiles = [double[0] for double in doubles_list]
                elif len(missing_suits) == 1:
                    if (at_least_one_special_group or one_or_nine_in_hand):
                        self.winning_tiles = [double[0] for double in doubles_list if double[0][1] in missing_suits]
            elif num_doubles == 1:
                if len(leftover_tiles) < 2:
                    print(self.hand)
                    print(leftover_tiles)
                    print(self.open_groups)
                    print(num_groups)
                    raise ValueError()
                if leftover_tiles[0][0] in [2, 8] and leftover_tiles[0] == leftover_tiles[1]:
                    #remaining is double 2 or 8 and another double
                    self.winning_tiles = [leftover_tiles[0], doubles_list[0][0]]
                else:
                    #remaining is 1 double and one set that is within 2 spaces of each other
                    if len(leftover_tiles) != 2:
                        print('BAD')
                        print(self.hand)
                        print(leftover_tiles)
                        print(self.open_groups)
                        print(num_groups)
                        raise ValueError()
                    if leftover_tiles[0][0] - leftover_tiles[1][0] >= -2 and leftover_tiles[0][0] - leftover_tiles[1][0] <= 2 and leftover_tiles[0][1] == leftover_tiles[1][1]:
                        candidate_tiles = self.get_missing_of_straight(leftover_tiles)
                        if at_least_one_special_group:
                            if len(missing_suits) == 1:
                                if candidate_tiles[0][1] in missing_suits:
                                    self.winning_tiles = candidate_tiles
                            else:
                                self.winning_tiles = candidate_tiles
                        elif at_least_one_flush:
                            if one_or_nine_in_hand:
                                if len(missing_suits) == 1:
                                    if candidate_tiles[0][1] in missing_suits:
                                        self.winning_tiles = candidate_tiles
                                else:
                                    self.winning_tiles = candidate_tiles
                            else:
                                if len(missing_suits) == 1:
                                    if candidate_tiles[0][1] in missing_suits:
                                        self.winning_tiles = [tile for tile in candidate_tiles if tile[0] in [1, 9]]
                                else:
                                    self.winning_tiles = [tile for tile in candidate_tiles if tile[0] in [1, 9]]
            elif num_groups == 4:
                #remaining is single and we just need another of it to make a double
                if ((one_or_nine_in_hand and at_least_one_flush) or at_least_one_special_group) and (leftover_tiles[0][0] not in [2, 8]) and (len(missing_suits) == 0 or missing_suits[0] == leftover_tiles[0][1]):
                    self.winning_tiles = leftover_tiles
        return self.winning_tiles

        
class Game:
    def __init__(self, player_list=None, env=None, MCTS=False, state=('start', None, None), RANDSEED=None):
        self.RANDSEED = RANDSEED
        self.MCTS = MCTS
        self.env = env if env else Environment(copy.deepcopy(TILES), num_players=4, seed=self.RANDSEED)
        self.game_end = False
        if player_list:
            self.player_list = player_list
        else:
            self.player_list = [Player() for i in range(self.env.num_players)]
            for player in self.player_list:
                for tile in self.env.draw(13):
                    player.add_to_hand(tile)
            self.current_player_draw()
            self.env.discard(self.player_list[self.env.current_player_idx].discard(self))
            self.player_list[self.env.current_player_idx].update_winning_tiles()
        if state[0] != 'start':
            self.set_state(state)

    def to_dict(self):
        json_out = copy.deepcopy(self.__dict__)
        json_out['env'] = self.env.__dict__
        json_out['player_list'] = [player.to_dict() for player in self.player_list]
        return json_out

    def to_json(self, json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def from_json(self, json_file_path):
        with open(json_file_path, 'r') as f:
            self.from_dict(json.load(f))
        
    def from_dict(self, dict_to_load):
        pl = self.player_list
        e = self.env
        tmp_loaded_dict = copy.deepcopy(dict_to_load)
        for tmp_player in tmp_loaded_dict['player_list']:
            tmp_player["hand"] = [tuple(tile) for tile in tmp_player["hand"]]
            tmp_player["open_groups"] = [([tuple(tile) for tile in open_group[0]], open_group[1]) for open_group in tmp_player["open_groups"]]
        tmp_loaded_dict['env']['discarded'] = [tuple(tile) for tile in tmp_loaded_dict['env']['discarded']]
        tmp_loaded_dict['env']['remaining'] = [tuple(tile) for tile in tmp_loaded_dict['env']['remaining']]
        tmp_loaded_dict['env']['opened_tiles_per_player'] = [[tuple(tile) for tile in player_tiles] for player_tiles in tmp_loaded_dict['env']['opened_tiles_per_player']]
        tmp_loaded_dict['env']['discarded_tiles_per_player'] = [[tuple(tile) for tile in player_tiles] for player_tiles in tmp_loaded_dict['env']['discarded_tiles_per_player']]
        self.__dict__ = tmp_loaded_dict
        e.__dict__ = self.__dict__['env']
        self.env = e
        for i, p in enumerate(self.player_list):
            pl[i].from_dict(p)
        self.player_list = pl

    def shuffle_game(self, hero_player_idx):
        used_tiles = self.env.discarded + self.player_list[hero_player_idx].hand + [tile for player in self.player_list for group in player.open_groups for tile in group[0]]
        possible_remaining_tiles = copy.deepcopy(TILES)
        for tile in used_tiles:
            possible_remaining_tiles.pop(possible_remaining_tiles.index(tile))
        random.seed(self.RANDSEED)
        random.shuffle(possible_remaining_tiles)
        if self.RANDSEED is not None:
                self.RANDSEED += 1
        for i in range(0,4):
            if i != hero_player_idx:
                num_tiles_to_select = 13 - 3*len(self.player_list[i].open_groups)
                self.player_list[i].hand = possible_remaining_tiles[0:num_tiles_to_select]
                del possible_remaining_tiles[:num_tiles_to_select]
        self.env.remaining = possible_remaining_tiles

    def set_state(self, state):
        if state[0] == 'do_pong':
            tiles_opened = state[1]
            self.env.current_player_idx = state[2]
            self.env.open_hand(tiles_opened)
            self.player_list[self.env.current_player_idx].update_score()
            if not self.player_list[self.env.current_player_idx].score < 1:
                self.game_end = True
                return
            self.env.discard(self.player_list[self.env.current_player_idx].discard(self))
            self.player_list[self.env.current_player_idx].update_winning_tiles()        
            for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
                if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                    self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                    self.player_list[i % self.env.num_players].update_score()
                    self.game_end = True
                    return
        elif state[0] == 'reject_pong':
            if state[2] + 1 > self.env.current_player_idx:
                i = state[2] + 1
            else:
                i = state[2] + 1 + self.env.num_players
            while i < self.env.current_player_idx + self.env.num_players:
                if not i + 1 % self.env.num_players == self.env.current_player_idx:
                    tiles_opened = self.player_list[i % self.env.num_players].do_pong(self, i % self.env.num_players)
                    if tiles_opened:
                        self.env.current_player_idx = i % self.env.num_players
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
            self.env.discard(self.player_list[self.env.current_player_idx].discard(self))
            self.player_list[self.env.current_player_idx].update_winning_tiles()        
            for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
                if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                    self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                    self.player_list[i % self.env.num_players].update_score()
                    self.game_end = True
                    return

        elif state[0] == 'do_chi':
            self.env.open_hand(state[1])
            self.player_list[self.env.current_player_idx].update_score()
            if not self.player_list[self.env.current_player_idx].score < 1:
                self.game_end = True
                return
            self.env.discard(self.player_list[self.env.current_player_idx].discard(self))
            self.player_list[self.env.current_player_idx].update_winning_tiles()        
            for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
                if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                    self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                    self.player_list[i % self.env.num_players].update_score()
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
            self.env.discard(self.player_list[self.env.current_player_idx].discard(self))
            self.player_list[self.env.current_player_idx].update_winning_tiles()        
            for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
                if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                    self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                    self.player_list[i % self.env.num_players].update_score()
                    self.game_end = True
                    return
        elif state[0] == 'after_discard':
            discard_tile = state[1]
            self.env.discard(discard_tile)
            self.player_list[self.env.current_player_idx].update_winning_tiles()
            for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
                if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                    self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                    self.player_list[i % self.env.num_players].update_score()
                    self.game_end = True
                    return
        
    def current_player_draw(self):
        self.player_list[self.env.current_player_idx].add_to_hand(self.env.draw(1)[0])

    def play_turn(self):
        self.env.current_player_idx = (self.env.current_player_idx + 1) % self.env.num_players
        i = self.env.current_player_idx
        assert(all(len(player.hand)+len(player.open_groups)*3 > 12 for player in self.player_list))
        while i < self.env.current_player_idx + self.env.num_players:
            if not i + 1 % self.env.num_players == self.env.current_player_idx:
                tiles_opened = self.player_list[i % self.env.num_players].do_pong(self, i % self.env.num_players)
                if tiles_opened:
                    self.env.current_player_idx = i % self.env.num_players
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
        assert(all(len(player.hand)+len(player.open_groups)*3 > 12 for player in self.player_list))
        self.player_list[self.env.current_player_idx].update_score()
        if not self.player_list[self.env.current_player_idx].score < 1:
            self.game_end = True
            return
        discard_tile = self.player_list[self.env.current_player_idx].discard(self)
        self.env.discard(discard_tile)
        assert(all(len(player.hand)+len(player.open_groups)*3 > 12 for player in self.player_list))
        self.player_list[self.env.current_player_idx].update_winning_tiles()        
        for i in range(self.env.current_player_idx, self.env.current_player_idx + self.env.num_players):
            if self.env.discarded[-1] in self.player_list[i % self.env.num_players].winning_tiles:
                self.player_list[i % self.env.num_players].add_to_hand(self.env.discarded.pop(-1))
                self.player_list[i % self.env.num_players].update_score()
                self.game_end = True
                return
    def play(self, num_turns_to_run=None):
        if num_turns_to_run is None:
            while not self.game_end:
                self.play_turn()
        else:
            i = 0
            while (not self.game_end) and (num_turns_to_run > i):
                self.play_turn()
                i += 1



class InteractiveGame:
    def __init__(self, starting_player_idx=None, my_hand=None, num_players=4, game=None):
        if not game==None:
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
        if tile is None and current_player_idx != 0:
            return {'Error': 'Tried to discard with None on non-user player with index {}'.format(current_player_idx)}
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



