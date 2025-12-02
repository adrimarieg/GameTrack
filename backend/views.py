from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
import json
from pathlib import Path

from .models import Player, Match, PlayerMatchStats
from .serializers import (
    PlayerSerializer,
    PlayerLookupSerializer,
    PlayerMatchHistorySerializer,
    PlayerMatchStatsSerializer
)

# Import existing backend functions
import sys
backend_path = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_path))

from backend.auth.riotAPI import RiotAPIClient
from get_stats.player_uiid import get_account
from get_stats.get_matches import get_matches_list
from get_stats.get_ten_matches_data import get_matches_data


@api_view(['POST'])
def lookup_player(request):
    """
    Look up a player by their Riot ID (game_name#tag_line)

    POST /api/players/search
    Body: {"game_name": "PlayerName", "tag_line": "NA1"}

    Returns player PUUID and basic info
    """
    serializer = PlayerLookupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    game_name = serializer.validated_data['game_name']
    tag_line = serializer.validated_data['tag_line']

    try:
        # Call Riot API to get account info
        api_client = RiotAPIClient(
            api_key=settings.RIOT_API_KEY,
            base_url="https://americas.api.riotgames.com"
        )

        endpoint = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = api_client.call_api(endpoint)

        if not response:
            return Response(
                {"error": "Player not found or Riot API error"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save or update player in database
        player, created = Player.objects.update_or_create(
            puuid=response['puuid'],
            defaults={
                'game_name': response['gameName'],
                'tag_line': response['tagLine']
            }
        )

        return Response(
            {
                "player": PlayerSerializer(player).data,
                "created": created
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": f"Error looking up player: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_player_matches(request, puuid):
    """
    Get match history for a player by PUUID

    GET /api/players/{puuid}/matches?limit=10

    Returns last N matches with detailed stats
    """
    try:
        # Get player from database
        try:
            player = Player.objects.get(puuid=puuid)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player not found. Please search for the player first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get limit from query params (default 10)
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 20)  # Cap at 20 matches

        # Initialize Riot API client
        api_client = RiotAPIClient(
            api_key=settings.RIOT_API_KEY,
            base_url="https://americas.api.riotgames.com"
        )

        # Fetch match IDs
        matches_endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        match_ids = api_client.call_api(matches_endpoint, params={"count": limit})

        if not match_ids:
            return Response(
                {"error": "No matches found or API error"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch detailed match data
        match_stats_list = []

        with transaction.atomic():
            for match_id in match_ids[:limit]:
                # Check if match already exists in DB
                existing_stats = PlayerMatchStats.objects.filter(
                    player=player,
                    match__match_id=match_id
                ).first()

                if existing_stats:
                    match_stats_list.append(existing_stats)
                    continue

                # Fetch match data from API
                match_endpoint = f"/lol/match/v5/matches/{match_id}"
                match_data = api_client.call_api(match_endpoint)

                if not match_data:
                    continue

                # Create or update Match object
                match, _ = Match.objects.update_or_create(
                    match_id=match_id,
                    defaults={
                        'game_creation': match_data['info']['gameCreation'],
                        'game_duration': match_data['info']['gameDuration'],
                        'game_mode': match_data['info']['gameMode'],
                        'game_type': match_data['info']['gameType'],
                        'raw_data': match_data
                    }
                )

                # Find player's stats in the match
                player_data = None
                for participant in match_data['info']['participants']:
                    if participant['puuid'] == puuid:
                        player_data = participant
                        break

                if not player_data:
                    continue

                # Extract challenges data
                challenges = player_data.get('challenges', {})

                # Create PlayerMatchStats
                stats = PlayerMatchStats.objects.create(
                    player=player,
                    match=match,
                    kills=player_data.get('kills', 0),
                    deaths=player_data.get('deaths', 0),
                    assists=player_data.get('assists', 0),
                    win=player_data.get('win', False),
                    champion_id=player_data.get('championId', 0),
                    champion_name=player_data.get('championName', ''),
                    champ_level=player_data.get('champLevel', 1),
                    double_kills=player_data.get('doubleKills', 0),
                    triple_kills=player_data.get('tripleKills', 0),
                    quadra_kills=player_data.get('quadraKills', 0),
                    penta_kills=player_data.get('pentaKills', 0),
                    total_damage_dealt_to_champions=player_data.get('totalDamageDealtToChampions', 0),
                    gold_earned=player_data.get('goldEarned', 0),
                    total_minions_killed=player_data.get('totalMinionsKilled', 0),
                    vision_score=player_data.get('visionScore', 0),
                    wards_placed=player_data.get('wardsPlaced', 0),
                    wards_killed=player_data.get('wardsKilled', 0),
                    kill_participation=challenges.get('killParticipation'),
                    damage_per_minute=challenges.get('damagePerMinute'),
                    gold_per_minute=challenges.get('goldPerMinute')
                )
                match_stats_list.append(stats)

        # Calculate summary statistics
        if match_stats_list:
            total_matches = len(match_stats_list)
            wins = sum(1 for s in match_stats_list if s.win)
            total_kills = sum(s.kills for s in match_stats_list)
            total_deaths = sum(s.deaths for s in match_stats_list)
            total_assists = sum(s.assists for s in match_stats_list)

            summary = {
                "total_matches": total_matches,
                "wins": wins,
                "losses": total_matches - wins,
                "win_rate": round((wins / total_matches) * 100, 1) if total_matches > 0 else 0,
                "avg_kills": round(total_kills / total_matches, 1) if total_matches > 0 else 0,
                "avg_deaths": round(total_deaths / total_matches, 1) if total_matches > 0 else 0,
                "avg_assists": round(total_assists / total_matches, 1) if total_matches > 0 else 0,
                "avg_kda": round(
                    (total_kills + total_assists) / total_deaths if total_deaths > 0 else (total_kills + total_assists),
                    2
                ),
                "avg_damage": round(
                    sum(s.total_damage_dealt_to_champions for s in match_stats_list) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_gold": round(
                    sum(s.gold_earned for s in match_stats_list) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_cs": round(
                    sum(s.total_minions_killed for s in match_stats_list) / total_matches, 1
                ) if total_matches > 0 else 0,
                "avg_vision_score": round(
                    sum(s.vision_score for s in match_stats_list) / total_matches, 1
                ) if total_matches > 0 else 0,
            }
        else:
            summary = {}

        # Serialize response
        response_data = {
            "player": PlayerSerializer(player).data,
            "matches": PlayerMatchStatsSerializer(match_stats_list, many=True).data,
            "total_matches": len(match_stats_list),
            "summary": summary
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Error fetching matches: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_cached_matches(request):
    """
    Read and transform cached match data from JSON files created by main.py

    GET /api/matches/cached

    Returns transformed match data in the format expected by the frontend
    """
    try:
        # Path to the JSON files in project root
        base_dir = Path(settings.BASE_DIR)
        matches_file = base_dir / 'dataTenMatches.json'

        # Check if file exists
        if not matches_file.exists():
            return Response(
                {"error": "No cached data found. Please run 'python main.py' first to fetch match data."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Read the cached match data
        with open(matches_file, 'r') as f:
            raw_matches = json.load(f)

        if not raw_matches:
            return Response(
                {"error": "Cached data is empty. Please run 'python main.py' to fetch fresh data."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the player's PUUID from the first match
        # The PUUID should be consistent across all matches
        first_match = raw_matches[0]
        # For now, we'll use a hardcoded PUUID that matches get_stats/get_matches.py
        player_puuid = "Ppd1Ebvndpxmp4swzT1zpl0ZKlIC4ydqw76oW49b_aAEGGqSdnWPPz-tUzRWcDdyAvFXkbXRpGw8B5Q"

        # Transform raw Riot API data into frontend format
        transformed_matches = []
        for match_data in raw_matches:
            match_info = match_data.get('info', {})

            # Find the player's participant data
            player_data = None
            for participant in match_info.get('participants', []):
                if participant.get('puuid') == player_puuid:
                    player_data = participant
                    break

            if not player_data:
                continue

            # Extract challenges data
            challenges = player_data.get('challenges', {})

            # Calculate KDA
            kills = player_data.get('kills', 0)
            deaths = player_data.get('deaths', 0)
            assists = player_data.get('assists', 0)
            kda = round((kills + assists) / deaths, 2) if deaths > 0 else kills + assists

            # Transform to frontend format
            match_stats = {
                "match_id": match_data.get('metadata', {}).get('matchId', ''),
                "game_datetime": str(match_info.get('gameCreation', 0)),
                "game_duration": match_info.get('gameDuration', 0),
                "game_mode": match_info.get('gameMode', ''),
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "win": player_data.get('win', False),
                "kda": kda,
                "champion_id": player_data.get('championId', 0),
                "champion_name": player_data.get('championName', ''),
                "champ_level": player_data.get('champLevel', 1),
                "double_kills": player_data.get('doubleKills', 0),
                "triple_kills": player_data.get('tripleKills', 0),
                "quadra_kills": player_data.get('quadraKills', 0),
                "penta_kills": player_data.get('pentaKills', 0),
                "total_damage_dealt_to_champions": player_data.get('totalDamageDealtToChampions', 0),
                "damage_per_minute": challenges.get('damagePerMinute'),
                "gold_earned": player_data.get('goldEarned', 0),
                "gold_per_minute": challenges.get('goldPerMinute'),
                "total_minions_killed": player_data.get('totalMinionsKilled', 0),
                "vision_score": player_data.get('visionScore', 0),
                "wards_placed": player_data.get('wardsPlaced', 0),
                "wards_killed": player_data.get('wardsKilled', 0),
                "kill_participation": challenges.get('killParticipation'),
                "created_at": "",
                "updated_at": ""
            }
            transformed_matches.append(match_stats)

        # Calculate summary statistics
        if transformed_matches:
            total_matches = len(transformed_matches)
            wins = sum(1 for m in transformed_matches if m['win'])
            total_kills = sum(m['kills'] for m in transformed_matches)
            total_deaths = sum(m['deaths'] for m in transformed_matches)
            total_assists = sum(m['assists'] for m in transformed_matches)

            summary = {
                "total_matches": total_matches,
                "wins": wins,
                "losses": total_matches - wins,
                "win_rate": round((wins / total_matches) * 100, 1) if total_matches > 0 else 0,
                "avg_kills": round(total_kills / total_matches, 1) if total_matches > 0 else 0,
                "avg_deaths": round(total_deaths / total_matches, 1) if total_matches > 0 else 0,
                "avg_assists": round(total_assists / total_matches, 1) if total_matches > 0 else 0,
                "avg_kda": round(
                    (total_kills + total_assists) / total_deaths if total_deaths > 0 else (total_kills + total_assists),
                    2
                ),
                "avg_damage": round(
                    sum(m['total_damage_dealt_to_champions'] for m in transformed_matches) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_gold": round(
                    sum(m['gold_earned'] for m in transformed_matches) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_cs": round(
                    sum(m['total_minions_killed'] for m in transformed_matches) / total_matches, 1
                ) if total_matches > 0 else 0,
                "avg_vision_score": round(
                    sum(m['vision_score'] for m in transformed_matches) / total_matches, 1
                ) if total_matches > 0 else 0,
            }
        else:
            summary = {}

        # Create player object (extracted from first match participant data)
        player_name = raw_matches[0]['info']['participants'][0].get('riotIdGameName', 'Player')
        player_tag = raw_matches[0]['info']['participants'][0].get('riotIdTagline', 'NA1')

        # Find the actual player's name from the matched participant
        for participant in raw_matches[0]['info']['participants']:
            if participant.get('puuid') == player_puuid:
                player_name = participant.get('riotIdGameName', 'Player')
                player_tag = participant.get('riotIdTagline', 'NA1')
                break

        player = {
            "puuid": player_puuid,
            "game_name": player_name,
            "tag_line": player_tag,
            "created_at": "",
            "updated_at": ""
        }

        # Construct response
        response_data = {
            "player": player,
            "matches": transformed_matches,
            "total_matches": len(transformed_matches),
            "summary": summary
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response(
            {"error": "Invalid JSON format in cached data file. Please run 'python main.py' to regenerate."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {"error": f"Error reading cached matches: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def fetch_player_stats(request):
    """
    Fetch player stats using the get_stats functions

    POST /api/players/fetch-stats
    Body: {"game_name": "PlayerName", "tag_line": "NA1", "limit": 10}

    This endpoint:
    1. Calls get_account() to get PUUID
    2. Calls get_matches_list() to get match IDs
    3. Calls get_matches_data() to get detailed match data
    4. Saves data to JSON files
    5. Returns transformed data to frontend
    """
    serializer = PlayerLookupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    game_name = serializer.validated_data['game_name']
    tag_line = serializer.validated_data['tag_line']
    limit = int(request.data.get('limit', 10))
    limit = min(limit, 20)  # Cap at 20 matches

    try:
        # Step 1: Get account info (PUUID)
        print(f"Fetching account info for {game_name}#{tag_line}...")
        account_data = get_account(game_name, tag_line)

        if not account_data:
            return Response(
                {"error": "Player not found or Riot API error"},
                status=status.HTTP_404_NOT_FOUND
            )

        player_puuid = account_data.get('puuid')
        if not player_puuid:
            return Response(
                {"error": "Failed to get player PUUID"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 2: Get match IDs
        print(f"Fetching match IDs for PUUID: {player_puuid}...")
        match_ids = get_matches_list(puuid=player_puuid, limit=limit)

        if not match_ids:
            return Response(
                {"error": "No matches found for this player"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Step 3: Get detailed match data
        print(f"Fetching detailed data for {len(match_ids)} matches...")
        raw_matches = get_matches_data(match_ids, limit=limit)

        if not raw_matches:
            return Response(
                {"error": "Failed to fetch match data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 4: Transform the data for frontend
        transformed_matches = []
        for match_data in raw_matches:
            match_info = match_data.get('info', {})

            # Find the player's participant data
            player_data = None
            for participant in match_info.get('participants', []):
                if participant.get('puuid') == player_puuid:
                    player_data = participant
                    break

            if not player_data:
                continue

            # Extract challenges data
            challenges = player_data.get('challenges', {})

            # Calculate KDA
            kills = player_data.get('kills', 0)
            deaths = player_data.get('deaths', 0)
            assists = player_data.get('assists', 0)
            kda = round((kills + assists) / deaths, 2) if deaths > 0 else kills + assists

            # Transform to frontend format
            match_stats = {
                "match_id": match_data.get('metadata', {}).get('matchId', ''),
                "game_datetime": str(match_info.get('gameCreation', 0)),
                "game_duration": match_info.get('gameDuration', 0),
                "game_mode": match_info.get('gameMode', ''),
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "win": player_data.get('win', False),
                "kda": kda,
                "champion_id": player_data.get('championId', 0),
                "champion_name": player_data.get('championName', ''),
                "champ_level": player_data.get('champLevel', 1),
                "double_kills": player_data.get('doubleKills', 0),
                "triple_kills": player_data.get('tripleKills', 0),
                "quadra_kills": player_data.get('quadraKills', 0),
                "penta_kills": player_data.get('pentaKills', 0),
                "total_damage_dealt_to_champions": player_data.get('totalDamageDealtToChampions', 0),
                "damage_per_minute": challenges.get('damagePerMinute'),
                "gold_earned": player_data.get('goldEarned', 0),
                "gold_per_minute": challenges.get('goldPerMinute'),
                "total_minions_killed": player_data.get('totalMinionsKilled', 0),
                "vision_score": player_data.get('visionScore', 0),
                "wards_placed": player_data.get('wardsPlaced', 0),
                "wards_killed": player_data.get('wardsKilled', 0),
                "kill_participation": challenges.get('killParticipation'),
                "created_at": "",
                "updated_at": ""
            }
            transformed_matches.append(match_stats)

        # Step 5: Calculate summary statistics
        if transformed_matches:
            total_matches = len(transformed_matches)
            wins = sum(1 for m in transformed_matches if m['win'])
            total_kills = sum(m['kills'] for m in transformed_matches)
            total_deaths = sum(m['deaths'] for m in transformed_matches)
            total_assists = sum(m['assists'] for m in transformed_matches)

            summary = {
                "total_matches": total_matches,
                "wins": wins,
                "losses": total_matches - wins,
                "win_rate": round((wins / total_matches) * 100, 1) if total_matches > 0 else 0,
                "avg_kills": round(total_kills / total_matches, 1) if total_matches > 0 else 0,
                "avg_deaths": round(total_deaths / total_matches, 1) if total_matches > 0 else 0,
                "avg_assists": round(total_assists / total_matches, 1) if total_matches > 0 else 0,
                "avg_kda": round(
                    (total_kills + total_assists) / total_deaths if total_deaths > 0 else (total_kills + total_assists),
                    2
                ),
                "avg_damage": round(
                    sum(m['total_damage_dealt_to_champions'] for m in transformed_matches) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_gold": round(
                    sum(m['gold_earned'] for m in transformed_matches) / total_matches, 0
                ) if total_matches > 0 else 0,
                "avg_cs": round(
                    sum(m['total_minions_killed'] for m in transformed_matches) / total_matches, 1
                ) if total_matches > 0 else 0,
                "avg_vision_score": round(
                    sum(m['vision_score'] for m in transformed_matches) / total_matches, 1
                ) if total_matches > 0 else 0,
            }
        else:
            summary = {}

        # Create player object
        player = {
            "puuid": player_puuid,
            "game_name": account_data.get('gameName', game_name),
            "tag_line": account_data.get('tagLine', tag_line),
            "created_at": "",
            "updated_at": ""
        }

        # Construct response
        response_data = {
            "player": player,
            "matches": transformed_matches,
            "total_matches": len(transformed_matches),
            "summary": summary
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"Error fetching player stats: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
