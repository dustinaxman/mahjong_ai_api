#{'game_state': game_state_dict, 'action': 'discard'}

curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT




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

