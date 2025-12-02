# GameTrack Class Diagram

This document contains a comprehensive UML class diagram for the GameTrack project, showing all classes, interfaces, their attributes, methods, and relationships.

## Full System Class Diagram

```mermaid
classDiagram
    %% ============================================
    %% BACKEND - DJANGO MODELS LAYER
    %% ============================================

    class Player {
        +CharField puuid PK
        +CharField game_name
        +CharField tag_line
        +DateTimeField created_at
        +DateTimeField updated_at
        +__str__() str
    }

    class Match {
        +CharField match_id PK
        +BigIntegerField game_creation
        +IntegerField game_duration
        +CharField game_mode
        +CharField game_type
        +JSONField raw_data
        +DateTimeField created_at
        +DateTimeField updated_at
        +game_datetime datetime
        +__str__() str
    }

    class PlayerMatchStats {
        +ForeignKey player
        +ForeignKey match
        +IntegerField kills
        +IntegerField deaths
        +IntegerField assists
        +BooleanField win
        +IntegerField champion_id
        +CharField champion_name
        +IntegerField champ_level
        +IntegerField double_kills
        +IntegerField triple_kills
        +IntegerField quadra_kills
        +IntegerField penta_kills
        +IntegerField total_damage_dealt_to_champions
        +IntegerField gold_earned
        +IntegerField total_minions_killed
        +IntegerField vision_score
        +IntegerField wards_placed
        +IntegerField wards_killed
        +FloatField kda
        +FloatField kill_participation
        +FloatField damage_per_minute
        +FloatField gold_per_minute
        +DateTimeField created_at
        +DateTimeField updated_at
        +save() void
        +__str__() str
    }

    %% Database Relationships
    Player "1" --> "0..*" PlayerMatchStats : has match_stats
    Match "1" --> "0..*" PlayerMatchStats : has player_stats
    PlayerMatchStats "0..*" --> "1" Player : belongs to
    PlayerMatchStats "0..*" --> "1" Match : belongs to

    %% ============================================
    %% BACKEND - API CLIENT LAYER
    %% ============================================

    class RiotAPIClient {
        -str api_key
        -str base_url
        +__init__(api_key, base_url)
        +call_api(endpoint, params, headers, method) dict
    }

    %% ============================================
    %% BACKEND - SERIALIZERS LAYER
    %% ============================================

    class PlayerSerializer {
        <<ModelSerializer>>
        +Meta model Player
        +Meta fields [puuid, game_name, tag_line, created_at, updated_at]
        +Meta read_only_fields [created_at, updated_at]
    }

    class MatchSerializer {
        <<ModelSerializer>>
        +DateTimeField game_datetime
        +Meta model Match
        +Meta fields [match_id, game_creation, game_datetime, game_duration, game_mode, game_type, created_at, updated_at]
        +Meta read_only_fields [created_at, updated_at]
    }

    class PlayerMatchStatsSerializer {
        <<ModelSerializer>>
        +CharField match_id
        +DateTimeField game_datetime
        +IntegerField game_duration
        +CharField game_mode
        +Meta model PlayerMatchStats
        +Meta read_only_fields [created_at, updated_at, kda]
    }

    class PlayerMatchHistorySerializer {
        <<Serializer>>
        +PlayerSerializer player
        +PlayerMatchStatsSerializer matches
        +IntegerField total_matches
        +DictField summary
    }

    class PlayerLookupSerializer {
        <<Serializer>>
        +CharField game_name
        +CharField tag_line
        +validate_game_name(value) str
        +validate_tag_line(value) str
    }

    %% Serializer Dependencies
    PlayerSerializer ..> Player : serializes
    MatchSerializer ..> Match : serializes
    PlayerMatchStatsSerializer ..> PlayerMatchStats : serializes
    PlayerMatchHistorySerializer ..> PlayerSerializer : uses
    PlayerMatchHistorySerializer ..> PlayerMatchStatsSerializer : uses

    %% ============================================
    %% BACKEND - VIEWS LAYER
    %% ============================================

    class ViewFunctions {
        <<module>>
        +lookup_player(request) Response
        +get_player_matches(request, puuid) Response
        +get_cached_matches(request) Response
        +fetch_player_stats(request) Response
    }

    %% View Dependencies
    ViewFunctions ..> RiotAPIClient : uses
    ViewFunctions ..> Player : queries
    ViewFunctions ..> Match : queries
    ViewFunctions ..> PlayerMatchStats : queries
    ViewFunctions ..> PlayerSerializer : serializes with
    ViewFunctions ..> PlayerMatchStatsSerializer : serializes with
    ViewFunctions ..> PlayerMatchHistorySerializer : serializes with
    ViewFunctions ..> PlayerLookupSerializer : validates with

    %% ============================================
    %% BACKEND - HELPER FUNCTIONS
    %% ============================================

    class HelperFunctions {
        <<module>>
        +get_account(game_name, tag_line) dict
        +get_matches_list(puuid, limit) list
        +get_matches_data(matchIDs, limit) list
    }

    HelperFunctions ..> RiotAPIClient : uses
    ViewFunctions ..> HelperFunctions : calls

    %% ============================================
    %% FRONTEND - TYPESCRIPT INTERFACES
    %% ============================================

    class Player_TS {
        <<interface>>
        +string puuid
        +string game_name
        +string tag_line
        +string created_at
        +string updated_at
    }

    class PlayerMatchStats_TS {
        <<interface>>
        +string match_id
        +string game_datetime
        +number game_duration
        +string game_mode
        +number kills
        +number deaths
        +number assists
        +boolean win
        +number|null kda
        +number champion_id
        +string champion_name
        +number champ_level
        +number double_kills
        +number triple_kills
        +number quadra_kills
        +number penta_kills
        +number total_damage_dealt_to_champions
        +number|null damage_per_minute
        +number gold_earned
        +number|null gold_per_minute
        +number total_minions_killed
        +number vision_score
        +number wards_placed
        +number wards_killed
        +number|null kill_participation
        +string created_at
        +string updated_at
    }

    class Summary_TS {
        <<interface>>
        +number total_matches
        +number wins
        +number losses
        +number win_rate
        +number avg_kills
        +number avg_deaths
        +number avg_assists
        +number avg_kda
        +number avg_damage
        +number avg_gold
        +number avg_cs
        +number avg_vision_score
    }

    class PlayerMatchHistoryResponse_TS {
        <<interface>>
        +Player_TS player
        +PlayerMatchStats_TS[] matches
        +number total_matches
        +Summary_TS summary
    }

    class PlayerLookupRequest_TS {
        <<interface>>
        +string game_name
        +string tag_line
    }

    class PlayerLookupResponse_TS {
        <<interface>>
        +Player_TS player
        +boolean created
    }

    class StatFilter_TS {
        <<interface>>
        +StatKey key
        +string label
        +string category
    }

    %% TypeScript Interface Relationships
    PlayerMatchHistoryResponse_TS ..> Player_TS : contains
    PlayerMatchHistoryResponse_TS ..> PlayerMatchStats_TS : contains
    PlayerMatchHistoryResponse_TS ..> Summary_TS : contains
    PlayerLookupResponse_TS ..> Player_TS : contains

    %% ============================================
    %% FRONTEND - API CLIENT
    %% ============================================

    class APIError {
        <<extends Error>>
        +string message
        +string name
        +number status
        +unknown data
        +constructor(message, status, data)
    }

    class APIClient {
        <<object>>
        +lookupPlayer(gameName, tagLine) Promise~PlayerLookupResponse_TS~
        +getPlayerMatches(puuid, limit) Promise~PlayerMatchHistoryResponse_TS~
        +searchPlayerAndGetMatches(gameName, tagLine, limit) Promise~PlayerMatchHistoryResponse_TS~
        +getCachedMatches() Promise~PlayerMatchHistoryResponse_TS~
        +fetchPlayerStats(gameName, tagLine, limit) Promise~PlayerMatchHistoryResponse_TS~
        -handleResponse(response) Promise~T~
    }

    APIClient ..> APIError : throws
    APIClient ..> PlayerLookupRequest_TS : uses
    APIClient ..> PlayerLookupResponse_TS : returns
    APIClient ..> PlayerMatchHistoryResponse_TS : returns

    %% ============================================
    %% FRONTEND - REACT COMPONENTS
    %% ============================================

    class RiotIDInput {
        <<component>>
        +Props onSubmit
        +Props isLoading
        -State gameName
        -State tagLine
        +handleSubmit(e) void
    }

    class StatsFilter {
        <<component>>
        +Props selectedStats
        +Props onChange
        +handleCheckboxChange(values) void
    }

    class SummaryCards {
        <<component>>
        +Props summary
    }

    class StatCard {
        <<component>>
        +Props label
        +Props value
        +Props subValue
        +Props colorScheme
    }

    class StatsLineChart {
        <<component>>
        +Props matches
        +Props selectedStats
    }

    class StatsBarChart {
        <<component>>
        +Props matches
        +Props selectedStats
    }

    class MainPage {
        <<component>>
        -State playerData
        -State isLoading
        -State selectedStats
        +handleSearch(gameName, tagLine) void
        +handleStatsChange(stats) void
    }

    %% Component Relationships
    SummaryCards ..> StatCard : renders
    SummaryCards ..> Summary_TS : uses
    StatsLineChart ..> PlayerMatchStats_TS : uses
    StatsBarChart ..> PlayerMatchStats_TS : uses
    StatsFilter ..> StatFilter_TS : uses

    MainPage ..> RiotIDInput : contains
    MainPage ..> StatsFilter : contains
    MainPage ..> SummaryCards : contains
    MainPage ..> StatsLineChart : contains
    MainPage ..> StatsBarChart : contains
    MainPage ..> APIClient : calls

    %% ============================================
    %% CROSS-LAYER DATA FLOW
    %% ============================================

    Player_TS -.-> Player : mirrors
    PlayerMatchStats_TS -.-> PlayerMatchStats : mirrors
    APIClient -.-> ViewFunctions : HTTP requests 

```

## Layer Breakdown

### Backend Layers

1. **Models Layer**: Django ORM models that represent database tables
   - `Player`: Stores player account information (PUUID, Riot ID)
   - `Match`: Stores match metadata (duration, mode, timestamps)
   - `PlayerMatchStats`: Stores detailed player performance in each match

2. **API Client Layer**: Integration with external APIs
   - `RiotAPIClient`: Handles Riot Games API calls with rate limiting and retry logic

3. **Serializers Layer**: Data transformation between Django models and JSON
   - `PlayerSerializer`, `MatchSerializer`, `PlayerMatchStatsSerializer`: Model serializers
   - `PlayerMatchHistorySerializer`: Composite response serializer
   - `PlayerLookupSerializer`: Request validation serializer

4. **Views Layer**: API endpoint handlers
   - `lookup_player()`: POST /api/players/search
   - `get_player_matches()`: GET /api/players/{puuid}/matches
   - `get_cached_matches()`: GET /api/matches/cached
   - `fetch_player_stats()`: POST /api/players/fetch-stats

5. **Helper Functions Layer**: Utility functions for data fetching
   - `get_account()`: Fetch player PUUID by Riot ID
   - `get_matches_list()`: Fetch match IDs for a player
   - `get_matches_data()`: Fetch detailed match data

### Frontend Layers

1. **TypeScript Types Layer**: Type definitions that mirror backend models
   - Interfaces for Player, PlayerMatchStats, Summary
   - Request/Response types for API calls
   - StatFilter type for UI state management

2. **API Client Layer**: HTTP client for backend communication
   - `APIClient`: Wrapper around fetch API with error handling
   - `APIError`: Custom error class for API failures

3. **React Components Layer**: UI components
   - `MainPage`: Root page component orchestrating all child components
   - `RiotIDInput`: Player search form
   - `StatsFilter`: Multi-select stat filter
   - `SummaryCards`: Performance summary cards grid
   - `StatsLineChart`: Line chart for stat trends
   - `StatsBarChart`: Bar chart for K/D/A comparison

## Key Relationships

### Database Relationships
- **One-to-Many**: `Player` → `PlayerMatchStats` (one player has many match stats)
- **One-to-Many**: `Match` → `PlayerMatchStats` (one match has many player stats)
- **Unique Constraint**: (`player`, `match`) in `PlayerMatchStats` (each player-match pair is unique)

### Data Flow
1. **Frontend → Backend**: React components call `APIClient` methods
2. **Backend Views → API Client**: Views use `RiotAPIClient` to fetch external data
3. **Backend Views → Models**: Views query/create database records
4. **Backend Models → Serializers**: Serializers transform model instances to JSON
5. **Backend → Frontend**: JSON responses consumed by TypeScript interfaces

### Type Mirroring
- TypeScript interfaces (`Player_TS`, `PlayerMatchStats_TS`) mirror Django models (`Player`, `PlayerMatchStats`)
- Ensures type safety across full stack
- Serializers act as the contract between backend and frontend

## API Endpoints Documentation

| Endpoint | Method | Request | Response | View Function |
|----------|--------|---------|----------|---------------|
| `/api/players/search` | POST | `PlayerLookupRequest` | `PlayerLookupResponse` | `lookup_player()` |
| `/api/players/{puuid}/matches` | GET | Query: `limit=10` | `PlayerMatchHistoryResponse` | `get_player_matches()` |
| `/api/matches/cached` | GET | - | `PlayerMatchHistoryResponse` | `get_cached_matches()` |
| `/api/players/fetch-stats` | POST | `PlayerLookupRequest + limit` | `PlayerMatchHistoryResponse` | `fetch_player_stats()` |

## Notes

- **Auto-calculation**: `PlayerMatchStats.kda` is automatically calculated in the model's `save()` method
- **Caching**: Matches and stats are cached in the database to reduce API calls
- **Rate Limiting**: `RiotAPIClient` implements automatic retry logic for 429 (Too Many Requests) responses
- **Type Safety**: Full TypeScript coverage on frontend ensures compile-time type checking
- **Responsive Design**: All React components use Chakra UI for mobile-friendly layouts
