import requests
import time
from keys import RIOT_API_KEY
from backend.auth.riotAPI import RiotAPIClient

def verify_summoner_name():
    verifiedSummonerName = False
    summoner_name = ""

    while verifiedSummonerName == False:
        summoner_name=input("Enter your summoner name: ")
        print(f"Is your summoner name: {summoner_name}?")
        userVerification=input("y/n")

        if userVerification == "y":
            print(f"Attempting authentication for summoner: {summoner_name}...")
            summoner_name = summoner_name.strip()
            verifiedSummonerName = True

    api = RiotAPIClient(api_key=RIOT_API_KEY, base_url="https://na1.api.riotgames.com")
    response = api.call_api(f"/lol/summoner/v4/summoners/by-name/{summoner_name}")
    print(response)
    
