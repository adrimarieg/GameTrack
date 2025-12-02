import requests
import json
from keys import APEX_API_KEY

def apex_api_call():

    player_name = ""
    PLATFORM = "PC"
    verified_username = False

    while verified_username == False:

        while player_name == "":
            player_name=input("Enter your Origin username: ")

        print(f"Is your username name: {player_name}?")

        user_verification=input("y/n")
        if user_verification == "y":
            print(f"Attempting authentication for: {player_name}...")
            player_name = player_name.strip()
            verified_username = True


    url = "https://api.mozambiquehe.re/bridge"
    params = {
        "auth": APEX_API_KEY,
        "player": player_name,
        "platform": PLATFORM
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        # with open('output.json', 'w') as f:
        #    json.dump(data, f, indent=4)
    else:
        print(f"API Error {response.status_code}: {response.text}")
