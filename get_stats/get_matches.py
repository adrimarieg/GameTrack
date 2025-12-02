import requests
import time
from keys import RIOT_API_KEY
from backend.auth.riotAPI import RiotAPIClient
import json

def get_matches_list(puuid=None, limit=10):
    """
    Get list of match IDs for a player

    Args:
        puuid: Player's PUUID
        limit: Number of matches to fetch (default: 10)

    Returns:
        list: List of match IDs
    """
    # If no PUUID provided, use hardcoded value for backward compatibility
    if puuid is None:
        puuid = "Ppd1Ebvndpxmp4swzT1zpl0ZKlIC4ydqw76oW49b_aAEGqSdnWPPz-tUzRWcDdyAvFXkbXRpGw8B5Q"

    print(f"Pulling last {limit} game data...")
    api = RiotAPIClient(api_key=RIOT_API_KEY, base_url="https://americas.api.riotgames.com")
    response = api.call_api(f"/lol/match/v5/matches/by-puuid/{puuid}/ids", params={"count": limit})
    data = response
    print("Saving matches...")
    with open('matchIDs.json', 'w') as f:
        json.dump(data, f, indent=4)

    return data
