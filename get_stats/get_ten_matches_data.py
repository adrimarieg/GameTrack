import requests
import time
from keys import RIOT_API_KEY
from backend.auth.riotAPI import RiotAPIClient
import json

def get_matches_data(matchIDs, limit=10):
    """
    Get detailed match data for a list of match IDs

    Args:
        matchIDs: List of match IDs to fetch
        limit: Maximum number of matches to fetch (default: 10)

    Returns:
        list: List of detailed match data
    """
    matches_data = []
    api = RiotAPIClient(api_key=RIOT_API_KEY, base_url="https://americas.api.riotgames.com")

    for matchId in matchIDs[:limit]:
        response = api.call_api(f"/lol/match/v5/matches/{matchId}")
        if response:
            matches_data.append(response)

    print(f"Data from your last {len(matches_data)} games have been saved!")

    with open('dataTenMatches.json', 'w') as f:
        json.dump(matches_data, f, indent=4)

    return matches_data