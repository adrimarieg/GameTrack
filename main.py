from get_stats.player_uiid import get_account
from get_stats.get_matches import get_matches_list
from get_stats.get_ten_matches_data import get_matches_data
import json


print("Welcome to GameTrack!")
# apex_api_call()
get_account()
get_matches_list()

# Load matchIDs from JSON file
with open('matchIDs.json', 'r') as f:
  matchIDs = json.load(f)

get_matches_data(matchIDs)