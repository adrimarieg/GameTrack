import requests
import time
from keys import RIOT_API_KEY
from backend.auth.riotAPI import RiotAPIClient

def get_account(game_name=None, tag_line=None):
    """
    Get account information by Riot ID

    Args:
        game_name: Player's game name (e.g., "PlayerName")
        tag_line: Player's tag line (e.g., "NA1")

    Returns:
        dict: Account data including PUUID
    """
    # If no parameters provided, prompt user for input (backward compatibility)
    if game_name is None or tag_line is None:
        riotID = ""
        confirmed = False

        gameName = ""

        while confirmed == False:
            riotID=input("Enter your RiotID: ")
            print(f"Is your RiotID: {riotID}?")
            userVerification=input("y/n")

            if userVerification == "y":
                print(f"Authenticating {riotID}...")
                gameName=riotID.strip()
                confirmed = True
    else:
        # Use provided parameters
        gameName = game_name.strip()
        tag_line = tag_line.strip()
        print(f"Authenticating {gameName}#{tag_line}...")

    api = RiotAPIClient(api_key=RIOT_API_KEY, base_url="https://americas.api.riotgames.com")

    # Use tag_line if provided, otherwise default to "NA1"
    tag = tag_line if tag_line else "NA1"
    response = api.call_api(f"/riot/account/v1/accounts/by-riot-id/{gameName}/{tag}")

    return response
