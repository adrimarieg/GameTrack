# GameTrack Sequence Diagrams

This document contains comprehensive sequence diagrams for all major workflows in the GameTrack project, showing component interactions, data flows, and error handling.

---

## 1. Complete Player Stats Search Flow (PRIMARY)

This is the main user journey through the application, from entering a Riot ID to viewing match statistics and charts.

**Key Features**:
- Full end-to-end flow from user input to data visualization
- Three sequential Riot API calls (account → match IDs → match details)
- Data transformation and summary statistics calculation
- Fresh data fetching (no database caching in this flow)

```mermaid
sequenceDiagram
    actor User
    participant RiotIDInput as RiotIDInput Component
    participant HomePage as Home Page Component
    participant APIClient as API Client
    participant DjangoView as fetch_player_stats View
    participant Serializer as PlayerLookupSerializer
    participant GetAccount as get_account()
    participant GetMatches as get_matches_list()
    participant GetData as get_matches_data()
    participant RiotAPI as RiotAPIClient
    participant Riot as Riot Games API
    participant UI as UI Components

    User->>RiotIDInput: Enter gameName & tagLine
    User->>RiotIDInput: Click "Search Player"
    activate RiotIDInput
    RiotIDInput->>RiotIDInput: Validate inputs (trim, check empty)
    RiotIDInput->>HomePage: onSubmit(gameName, tagLine)
    deactivate RiotIDInput

    activate HomePage
    HomePage->>HomePage: setIsLoading(true)
    HomePage->>HomePage: setError(null)
    HomePage->>UI: Show loading spinner

    HomePage->>APIClient: fetchPlayerStats(gameName, tagLine, 10)
    deactivate HomePage

    activate APIClient
    APIClient->>DjangoView: POST /api/players/fetch-stats<br/>{game_name, tag_line, limit: 10}
    deactivate APIClient

    activate DjangoView
    DjangoView->>Serializer: Validate request data
    activate Serializer
    Serializer->>Serializer: Strip whitespace from game_name
    Serializer->>Serializer: Remove '#' from tag_line
    Serializer->>Serializer: Validate non-empty
    alt Validation fails
        Serializer-->>DjangoView: Validation errors
        DjangoView-->>APIClient: 400 Bad Request
        APIClient-->>HomePage: Throw APIError
        HomePage->>UI: Show error alert
    end
    Serializer-->>DjangoView: Valid data
    deactivate Serializer

    Note over DjangoView: Cap limit at min(limit, 20)

    DjangoView->>GetAccount: get_account(game_name, tag_line)
    activate GetAccount
    GetAccount->>RiotAPI: Create RiotAPIClient
    GetAccount->>RiotAPI: call_api(/riot/account/v1/accounts/by-riot-id/{name}/{tag})
    activate RiotAPI
    RiotAPI->>Riot: GET account by Riot ID<br/>Header: X-Riot-Token
    activate Riot

    alt Rate Limited (429)
        Riot-->>RiotAPI: 429 + Retry-After header
        RiotAPI->>RiotAPI: Sleep(Retry-After seconds)
        RiotAPI->>Riot: Retry request (up to 3 attempts)
    end

    Riot-->>RiotAPI: 200 OK + {puuid, gameName, tagLine}
    deactivate Riot
    RiotAPI-->>GetAccount: {puuid, gameName, tagLine}
    deactivate RiotAPI
    GetAccount-->>DjangoView: account_data
    deactivate GetAccount

    alt Account not found
        DjangoView-->>APIClient: 404 Not Found
        APIClient-->>HomePage: Throw APIError
        HomePage->>UI: Show error: "Player not found"
    end

    Note over DjangoView: Extract player_puuid from account_data

    DjangoView->>GetMatches: get_matches_list(puuid, limit=10)
    activate GetMatches
    GetMatches->>RiotAPI: Create RiotAPIClient
    GetMatches->>RiotAPI: call_api(/lol/match/v5/matches/by-puuid/{puuid}/ids, {count: 10})
    activate RiotAPI
    RiotAPI->>Riot: GET match IDs<br/>Header: X-Riot-Token
    activate Riot
    Riot-->>RiotAPI: 200 OK + ["NA1_123...", "NA1_456...", ...]
    deactivate Riot
    RiotAPI-->>GetMatches: List of match IDs
    deactivate RiotAPI
    GetMatches->>GetMatches: Save to matchIDs.json
    GetMatches-->>DjangoView: match_ids[]
    deactivate GetMatches

    alt No matches found
        DjangoView-->>APIClient: 404 Not Found
        APIClient-->>HomePage: Throw APIError
        HomePage->>UI: Show error: "No matches found"
    end

    DjangoView->>GetData: get_matches_data(match_ids, limit=10)
    activate GetData
    GetData->>GetData: Create RiotAPIClient

    loop For each match_id in match_ids
        GetData->>RiotAPI: call_api(/lol/match/v5/matches/{match_id})
        activate RiotAPI
        RiotAPI->>Riot: GET match details<br/>Header: X-Riot-Token
        activate Riot
        Riot-->>RiotAPI: 200 OK + Full match data
        deactivate Riot
        RiotAPI-->>GetData: match_data
        deactivate RiotAPI
        GetData->>GetData: Append to matches_data[]
    end

    GetData->>GetData: Save to dataTenMatches.json
    GetData-->>DjangoView: raw_matches[]
    deactivate GetData

    Note over DjangoView: Transform match data for frontend

    loop For each match in raw_matches
        DjangoView->>DjangoView: Find player in participants[]
        DjangoView->>DjangoView: Extract stats (kills, deaths, assists, etc.)
        DjangoView->>DjangoView: Calculate KDA = (K+A)/D or K+A if D=0
        DjangoView->>DjangoView: Extract challenges (multikills, vision, etc.)
        DjangoView->>DjangoView: Calculate damage_per_minute, gold_per_minute
        DjangoView->>DjangoView: Append to transformed_matches[]
    end

    Note over DjangoView: Calculate summary statistics
    DjangoView->>DjangoView: total_matches = len(transformed_matches)
    DjangoView->>DjangoView: wins = count where win=true
    DjangoView->>DjangoView: losses = total - wins
    DjangoView->>DjangoView: win_rate = (wins/total) * 100
    DjangoView->>DjangoView: Calculate averages (KDA, kills, deaths, damage, gold, CS, vision)

    DjangoView-->>APIClient: 200 OK + PlayerMatchHistoryResponse<br/>{player, matches[], summary}
    deactivate DjangoView

    activate APIClient
    APIClient->>APIClient: Parse JSON response
    APIClient-->>HomePage: PlayerMatchHistoryResponse
    deactivate APIClient

    activate HomePage
    HomePage->>HomePage: setPlayerData(data)
    HomePage->>HomePage: setIsLoading(false)
    HomePage->>UI: Hide loading spinner

    HomePage->>UI: Render SummaryCards with summary stats
    activate UI
    UI->>UI: Display 8 stat cards (wins, losses, win_rate, avg_kda, etc.)
    deactivate UI

    HomePage->>UI: Render StatsLineChart with matches + selectedStats
    activate UI
    UI->>UI: Filter out 'win' stat
    UI->>UI: Reverse match order (oldest → newest)
    UI->>UI: Plot line chart with Recharts
    deactivate UI

    HomePage->>UI: Render StatsBarChart with matches + selectedStats
    activate UI
    UI->>UI: Filter to K/D/A stats
    UI->>UI: Color-code by win/loss
    UI->>UI: Plot bar chart with Recharts
    deactivate UI

    deactivate HomePage

    User->>User: View stats, charts, and performance summary
```

---

## 2. Player Lookup Only Flow

This flow handles looking up a player by Riot ID and creating/updating the player record in the database without fetching match history.

**Key Features**:
- Single Riot API call for account lookup
- Database upsert operation (create or update)
- Returns player info + created flag
- Used by `searchPlayerAndGetMatches()` composite method

```mermaid
sequenceDiagram
    participant APIClient as API Client
    participant DjangoView as lookup_player View
    participant Serializer as PlayerLookupSerializer
    participant RiotAPI as RiotAPIClient
    participant Riot as Riot Games API
    participant DB as Django ORM / Database
    participant PlayerSerializer as PlayerSerializer

    APIClient->>DjangoView: POST /api/players/search<br/>{game_name, tag_line}
    activate DjangoView

    DjangoView->>Serializer: Validate request data
    activate Serializer
    Serializer->>Serializer: validate_game_name(): strip, check not empty
    Serializer->>Serializer: validate_tag_line(): strip, remove '#', check not empty

    alt Validation fails
        Serializer-->>DjangoView: ValidationError
        DjangoView-->>APIClient: 400 Bad Request<br/>{error, field_errors}
        Note over APIClient: Throw APIError
    end

    Serializer-->>DjangoView: Validated data
    deactivate Serializer

    DjangoView->>RiotAPI: Create RiotAPIClient<br/>(api_key, base_url)
    DjangoView->>RiotAPI: call_api(/riot/account/v1/accounts/by-riot-id/{name}/{tag})
    activate RiotAPI

    RiotAPI->>Riot: GET account by Riot ID<br/>Header: X-Riot-Token
    activate Riot

    alt Success
        Riot-->>RiotAPI: 200 OK<br/>{puuid, gameName, tagLine}
    else Rate Limited
        Riot-->>RiotAPI: 429 + Retry-After
        RiotAPI->>RiotAPI: Sleep(Retry-After)
        RiotAPI->>Riot: Retry (up to 3 attempts)
    else Not Found
        Riot-->>RiotAPI: 404 Not Found
    end

    deactivate Riot
    RiotAPI-->>DjangoView: response or None
    deactivate RiotAPI

    alt Response is None
        DjangoView-->>APIClient: 404 Not Found<br/>{error: "Player not found or Riot API error"}
        Note over APIClient: Throw APIError
    end

    Note over DjangoView: Database upsert operation
    DjangoView->>DB: Player.objects.update_or_create(<br/>  puuid=response['puuid'],<br/>  defaults={game_name, tag_line}<br/>)
    activate DB

    DB->>DB: SELECT * FROM players<br/>WHERE puuid = '{puuid}'

    alt Player exists
        DB->>DB: UPDATE players SET<br/>game_name='{name}', tag_line='{tag}'<br/>WHERE puuid='{puuid}'
        DB-->>DjangoView: (Player instance, created=False)
    else Player doesn't exist
        DB->>DB: INSERT INTO players<br/>(puuid, game_name, tag_line, timestamps)
        DB-->>DjangoView: (Player instance, created=True)
    end

    deactivate DB

    DjangoView->>PlayerSerializer: PlayerSerializer(player).data
    activate PlayerSerializer
    PlayerSerializer-->>DjangoView: Serialized player data
    deactivate PlayerSerializer

    DjangoView-->>APIClient: 200 OK<br/>{player: {puuid, game_name, tag_line, timestamps}, created: bool}
    deactivate DjangoView

    Note over APIClient: Return PlayerLookupResponse
```

---

## 3. Match History Retrieval with Database Caching

This flow demonstrates the performance-optimized match history retrieval that checks the database cache before making external API calls.

**Key Features**:
- Player must already exist in database
- Check cache for each match before fetching from Riot API
- Partial cache support (some cached, some fresh)
- Transaction-wrapped database operations for atomicity
- Significantly faster for repeat queries

```mermaid
sequenceDiagram
    participant APIClient as API Client
    participant DjangoView as get_player_matches View
    participant DB as Django ORM / Database
    participant RiotAPI as RiotAPIClient
    participant Riot as Riot Games API
    participant Serializer as Serializers

    APIClient->>DjangoView: GET /api/players/{puuid}/matches?limit=10
    activate DjangoView

    DjangoView->>DjangoView: Extract limit from query params
    Note over DjangoView: limit = min(limit, 20)

    DjangoView->>DB: Player.objects.get(puuid=puuid)
    activate DB

    alt Player not found
        DB-->>DjangoView: Player.DoesNotExist
        DjangoView-->>APIClient: 404 Not Found<br/>{error: "Player not found. Please search first."}
    end

    DB-->>DjangoView: Player instance
    deactivate DB

    DjangoView->>RiotAPI: Create RiotAPIClient
    DjangoView->>RiotAPI: call_api(/lol/match/v5/matches/by-puuid/{puuid}/ids, {count: limit})
    activate RiotAPI
    RiotAPI->>Riot: GET match IDs
    activate Riot
    Riot-->>RiotAPI: 200 OK + match_ids[]
    deactivate Riot
    RiotAPI-->>DjangoView: match_ids[]
    deactivate RiotAPI

    alt No match IDs
        DjangoView-->>APIClient: 404 Not Found<br/>{error: "No matches found"}
    end

    Note over DjangoView: Begin database transaction
    DjangoView->>DB: BEGIN TRANSACTION
    activate DB

    DjangoView->>DjangoView: match_stats_list = []

    loop For each match_id in match_ids
        Note over DjangoView: Check database cache first
        DjangoView->>DB: PlayerMatchStats.objects.filter(<br/>  player=player,<br/>  match__match_id=match_id<br/>).first()

        alt Cache HIT
            DB-->>DjangoView: Existing PlayerMatchStats
            Note over DjangoView: Use cached data
            DjangoView->>DjangoView: Append to match_stats_list
            Note over DjangoView: Skip API call for this match
        else Cache MISS
            DB-->>DjangoView: None

            Note over DjangoView: Fetch from Riot API
            DjangoView->>RiotAPI: call_api(/lol/match/v5/matches/{match_id})
            activate RiotAPI
            RiotAPI->>Riot: GET match details
            activate Riot
            Riot-->>RiotAPI: 200 OK + match_data
            deactivate Riot
            RiotAPI-->>DjangoView: match_data
            deactivate RiotAPI

            alt API call failed
                Note over DjangoView: Continue to next match
            end

            Note over DjangoView: Create/update Match record
            DjangoView->>DB: Match.objects.update_or_create(<br/>  match_id=match_id,<br/>  defaults={game_creation, duration, mode, type, raw_data}<br/>)
            DB->>DB: SELECT/INSERT/UPDATE matches
            DB-->>DjangoView: (Match instance, created)

            Note over DjangoView: Find player in participants
            DjangoView->>DjangoView: Extract player_data from participants[]

            alt Player not in match
                Note over DjangoView: Continue to next match
            end

            Note over DjangoView: Extract all stats from player_data
            DjangoView->>DjangoView: Extract kills, deaths, assists, win, champion
            DjangoView->>DjangoView: Extract challenges (multikills, vision, etc.)
            DjangoView->>DjangoView: Extract combat, economy stats

            Note over DjangoView: Create PlayerMatchStats record
            DjangoView->>DB: PlayerMatchStats.objects.create(<br/>  player=player, match=match,<br/>  kills, deaths, assists, win,<br/>  champion_id, champion_name,<br/>  all other stats...<br/>)
            DB->>DB: Calculate KDA in save() method
            Note over DB: kda = (K+A)/D or K+A if D=0
            DB->>DB: INSERT INTO player_match_stats
            DB-->>DjangoView: stats instance

            DjangoView->>DjangoView: Append stats to match_stats_list
        end
    end

    DjangoView->>DB: COMMIT TRANSACTION
    Note over DB: All changes committed atomically
    deactivate DB

    alt No match stats retrieved
        DjangoView-->>APIClient: 200 OK with empty matches[]
    end

    Note over DjangoView: Calculate summary statistics
    DjangoView->>DjangoView: Calculate total_matches, wins, losses
    DjangoView->>DjangoView: Calculate win_rate = (wins/total) * 100
    DjangoView->>DjangoView: Calculate averages (KDA, kills, deaths, damage, gold, CS, vision)

    DjangoView->>Serializer: PlayerSerializer(player).data
    activate Serializer
    Serializer-->>DjangoView: Serialized player
    deactivate Serializer

    DjangoView->>Serializer: PlayerMatchStatsSerializer(match_stats_list, many=True).data
    activate Serializer
    Note over Serializer: Includes nested match data:<br/>match_id, game_datetime,<br/>game_duration, game_mode
    Serializer-->>DjangoView: Serialized matches
    deactivate Serializer

    DjangoView-->>APIClient: 200 OK<br/>PlayerMatchHistoryResponse<br/>{player, matches[], total_matches, summary}
    deactivate DjangoView
```

---

## 4. Rate Limit Handling & Retry Logic

This diagram shows the critical retry logic in `RiotAPIClient.call_api()` that handles Riot API rate limiting.

**Key Features**:
- Up to 3 retry attempts per request
- Respects `Retry-After` header from Riot API
- Handles both per-second and per-2-minute rate limits
- Exponential backoff via Retry-After values

```mermaid
sequenceDiagram
    participant Caller as Caller (View/Helper)
    participant RiotAPI as RiotAPIClient
    participant Time as time.sleep()
    participant Riot as Riot Games API

    Caller->>RiotAPI: call_api(endpoint, params, headers, method)
    activate RiotAPI

    Note over RiotAPI: Construct full URL<br/>Add X-Riot-Token header

    loop Retry loop: attempt = 0 to 2 (max 3 attempts)
        Note over RiotAPI: Attempt #{attempt + 1}

        RiotAPI->>Riot: HTTP Request<br/>{method} {url}<br/>Headers: X-Riot-Token
        activate Riot

        alt Success (200 OK)
            Riot-->>RiotAPI: 200 OK + JSON response
            deactivate Riot
            RiotAPI->>RiotAPI: Parse response.json()
            RiotAPI-->>Caller: Return parsed JSON
            Note over Caller: Success - exit function

        else Rate Limited (429)
            Riot-->>RiotAPI: 429 Too Many Requests<br/>Headers: {Retry-After: X}
            deactivate Riot

            Note over RiotAPI: Extract Retry-After header
            RiotAPI->>RiotAPI: retry_after = int(headers.get('Retry-After', 1))

            Note over RiotAPI,Time: Respect rate limit by sleeping
            RiotAPI->>Time: sleep(retry_after seconds)
            activate Time
            Note over Time: Thread blocks for {retry_after}s<br/>Typical values: 1-120 seconds
            Time-->>RiotAPI: Wake up
            deactivate Time

            Note over RiotAPI: Continue to next iteration<br/>Will retry the same request

        else Client Error (4xx) or Server Error (5xx)
            Riot-->>RiotAPI: 4xx or 5xx error
            deactivate Riot
            Note over RiotAPI: Non-retryable error
            RiotAPI->>RiotAPI: Break retry loop
            Note over RiotAPI: Exit loop, return None
        end
    end

    alt All retries exhausted OR non-retryable error
        RiotAPI-->>Caller: Return None
        deactivate RiotAPI
        Note over Caller: Handle None response<br/>(return 404/500 error)
    end
```

**Rate Limit Scenarios**:

```mermaid
sequenceDiagram
    participant RiotAPI as RiotAPIClient
    participant Riot as Riot Games API

    Note over RiotAPI,Riot: Scenario 1: First Attempt Success
    RiotAPI->>Riot: Request (attempt 1)
    Riot-->>RiotAPI: 200 OK
    Note over RiotAPI: Returns immediately, no retry

    Note over RiotAPI,Riot: Scenario 2: One Retry Success
    RiotAPI->>Riot: Request (attempt 1)
    Riot-->>RiotAPI: 429, Retry-After: 2
    RiotAPI->>RiotAPI: Sleep 2 seconds
    RiotAPI->>Riot: Request (attempt 2)
    Riot-->>RiotAPI: 200 OK
    Note over RiotAPI: Success after 1 retry

    Note over RiotAPI,Riot: Scenario 3: All Retries Failed
    RiotAPI->>Riot: Request (attempt 1)
    Riot-->>RiotAPI: 429, Retry-After: 1
    RiotAPI->>RiotAPI: Sleep 1 second
    RiotAPI->>Riot: Request (attempt 2)
    Riot-->>RiotAPI: 429, Retry-After: 2
    RiotAPI->>RiotAPI: Sleep 2 seconds
    RiotAPI->>Riot: Request (attempt 3)
    Riot-->>RiotAPI: 429, Retry-After: 5
    Note over RiotAPI: All 3 attempts failed<br/>Return None

    Note over RiotAPI,Riot: Scenario 4: Non-Retryable Error
    RiotAPI->>Riot: Request (attempt 1)
    Riot-->>RiotAPI: 404 Not Found
    Note over RiotAPI: Break immediately<br/>Return None (no retry)
```

---

## 5. Error Handling & User Feedback Flow

This diagram shows how errors from any source are caught, transformed, and displayed to the user with appropriate feedback.

**Key Features**:
- Multiple error sources (validation, network, API, server)
- APIError custom error class for structured errors
- Type-safe error handling in TypeScript
- User-friendly error messages in UI

```mermaid
sequenceDiagram
    participant User
    participant HomePage as Home Page Component
    participant APIClient as API Client
    participant Backend as Django Backend
    participant Alert as Chakra UI Alert

    User->>HomePage: Trigger search (with error condition)
    activate HomePage

    HomePage->>HomePage: try { handleSearch() }
    HomePage->>HomePage: setIsLoading(true)
    HomePage->>HomePage: setError(null)

    HomePage->>APIClient: fetchPlayerStats(gameName, tagLine, limit)
    deactivate HomePage

    activate APIClient

    alt Error Source 1: HTTP Error Response
        APIClient->>Backend: POST /api/players/fetch-stats
        activate Backend

        alt Validation Error (400)
            Backend-->>APIClient: 400 Bad Request<br/>{error: "Validation failed", details: {...}}
        else Not Found (404)
            Backend-->>APIClient: 404 Not Found<br/>{error: "Player not found or Riot API error"}
        else Server Error (500)
            Backend-->>APIClient: 500 Internal Server Error<br/>{error: "Error fetching player stats: ..."}
        end

        deactivate Backend

        APIClient->>APIClient: handleResponse(response)
        Note over APIClient: Check: if (!response.ok)

        APIClient->>APIClient: Try parse response.json()
        alt JSON parsing succeeds
            APIClient->>APIClient: errorData = await response.json()
        else JSON parsing fails
            APIClient->>APIClient: errorData = await response.text()
        end

        APIClient->>APIClient: Create APIError instance
        Note over APIClient: new APIError(<br/>  errorData?.error || "HTTP {status}",<br/>  response.status,<br/>  errorData<br/>)

        APIClient-->>HomePage: Throw APIError

    else Error Source 2: Network Failure
        APIClient->>Backend: POST /api/players/fetch-stats
        Note over Backend: Network timeout or unavailable
        APIClient->>APIClient: Fetch throws Error
        APIClient-->>HomePage: Throw Error (not APIError)

    else Error Source 3: Unexpected Exception
        APIClient->>APIClient: Unexpected error in try block
        APIClient-->>HomePage: Throw Error
    end

    deactivate APIClient

    activate HomePage
    Note over HomePage: catch (err) block executes

    HomePage->>HomePage: Check error type

    alt err instanceof APIError
        Note over HomePage: Structured API error
        HomePage->>HomePage: Extract err.message
        HomePage->>HomePage: setError(err.message)
        Note over HomePage: Examples:<br/>"Player not found or Riot API error"<br/>"Validation failed"<br/>"Error fetching player stats: ..."

    else Generic Error
        Note over HomePage: Network or unexpected error
        HomePage->>HomePage: setError('An unexpected error occurred. Please try again.')
    end

    HomePage->>HomePage: console.error('Error:', err)
    Note over HomePage: Log for debugging

    Note over HomePage: finally block executes
    HomePage->>HomePage: setIsLoading(false)

    HomePage->>Alert: Render error Alert (conditional)
    activate Alert

    Note over Alert: {error && <Alert>...}
    Alert->>Alert: Alert.Root status="error"
    Alert->>Alert: Alert.Indicator (error icon)
    Alert->>Alert: Alert.Title: "Error"
    Alert->>Alert: Alert.Description: {error message}

    Alert-->>User: Display red error alert
    deactivate Alert
    deactivate HomePage

    Note over User: User reads error message

    alt Error Recovery Path
        User->>HomePage: Correct input / Retry
        activate HomePage
        HomePage->>HomePage: setError(null)
        Note over HomePage: Error alert disappears
        HomePage->>HomePage: setPlayerData(null)
        HomePage->>HomePage: setIsLoading(true)
        HomePage->>APIClient: Retry API call
        deactivate HomePage
        Note over User,APIClient: New search attempt begins
    end
```

**Error Message Mapping**:

| Error Type | Status | Source | User Message |
|------------|--------|--------|--------------|
| Validation Error | 400 | Backend validation | Field-specific errors from serializer |
| Player Not Found | 404 | Riot API / Database | "Player not found or Riot API error" |
| No Matches | 404 | Riot API | "No matches found for this player" |
| Rate Limit Exhausted | 500 | Riot API (after retries) | "Error fetching player stats: ..." |
| Server Error | 500 | Backend exception | "Error fetching player stats: {details}" |
| Network Error | - | Fetch API | "An unexpected error occurred. Please try again." |
| Parse Error | - | JSON.parse() | "An unexpected error occurred. Please try again." |

**Error State Flow**:

```mermaid
stateDiagram-v2
    [*] --> Idle: Initial state
    Idle --> Loading: User submits search
    Loading --> Success: API returns 200 OK
    Loading --> Error: Any error occurs

    Success --> Idle: User clears data
    Success --> Loading: User searches again

    Error --> Loading: User retries
    Error --> Idle: User cancels

    Success: playerData populated<br/>Charts rendered<br/>error = null

    Loading: isLoading = true<br/>Spinner visible<br/>error = null

    Error: error message set<br/>Red alert visible<br/>isLoading = false

    Idle: No data<br/>No error<br/>Input ready
```

---

## Workflow Summary

### Data Flow Overview

```mermaid
graph LR
    User[User Input] --> Frontend[Frontend Components]
    Frontend --> API[API Client]
    API --> Django[Django Views]
    Django --> Helpers[Helper Functions]
    Helpers --> RiotClient[RiotAPIClient]
    RiotClient --> External[Riot Games API]

    Django --> DB[(Database)]
    DB --> Django

    External --> RiotClient
    RiotClient --> Helpers
    Helpers --> Django
    Django --> Serializers[Serializers]
    Serializers --> API
    API --> Frontend
    Frontend --> UI[UI Components]
    UI --> User

    style User fill:#e1f5ff
    style Frontend fill:#b3e5fc
    style Django fill:#81d4fa
    style DB fill:#4fc3f7
    style External fill:#29b6f6
    style UI fill:#e1f5ff
```

### Key Timing Characteristics

| Workflow | API Calls | DB Queries | Typical Duration |
|----------|-----------|------------|------------------|
| **Complete Player Stats Search** | 3 (account + match IDs + 10 matches) | 0 (no caching) | 3-10 seconds |
| **Player Lookup Only** | 1 (account) | 1 upsert | 0.5-2 seconds |
| **Match History (Full Cache)** | 1 (match IDs only) | ~20 SELECT queries | 0.2-1 second |
| **Match History (No Cache)** | 12 (match IDs + 10 matches + match upsert) | ~40 INSERT/SELECT queries | 3-8 seconds |
| **Match History (Partial Cache)** | 1 + N (N = uncached matches) | Mixed SELECT/INSERT | 1-5 seconds |

### Caching Strategy

- **Workflow 1 (fetch_player_stats)**: No database caching, always fetches fresh data
- **Workflow 3 (get_player_matches)**: Database caching with smart cache checking
- **Cache Key**: `(player_puuid, match_id)` unique constraint
- **Cache Invalidation**: None (data persists indefinitely)
- **Cache Benefits**:
  - Reduces Riot API calls by ~90% for repeat queries
  - Faster response times (0.2s vs 5s)
  - Reduces risk of rate limiting

### Rate Limiting Details

**Riot API Limits**:
- Development Key: 20 requests/second, 100 requests/2 minutes
- Production Key: Higher limits (varies by tier)

**GameTrack Handling**:
- **Reactive**: Responds to 429 errors, doesn't prevent them
- **Retry Strategy**: Up to 3 attempts with sleep between
- **Sleep Duration**: Dictated by `Retry-After` header (1-120 seconds)
- **Fallback**: Returns None if all retries fail

**Potential Issues**:
- Fetching 10 matches = 12 API calls (can hit rate limit)
- No request queuing or proactive throttling
- Each retry adds significant delay to user experience

### Transaction Boundaries

**Workflow 3 Match Processing**:
```python
with transaction.atomic():
    for match_id in match_ids:
        # Check cache
        # Fetch from API if needed
        # Create Match record
        # Create PlayerMatchStats record
# COMMIT - All or nothing
```

**Benefits**:
- Ensures database consistency
- Prevents partial data on errors
- Atomic rollback on exceptions

---

## Notes

- **Async Operations**: All HTTP requests (frontend fetch, backend requests) are asynchronous
- **Sync Operations**: Database queries, data transformation, calculations are synchronous
- **Error Propagation**: Errors bubble up from RiotAPI → Helpers → Views → APIClient → Components → UI
- **Type Safety**: TypeScript interfaces ensure type checking across frontend/backend boundary
- **Idempotency**: Player lookup is idempotent (update_or_create), match fetching is idempotent (check cache first)

