# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GameTrack is a full-stack gaming statistics tracker with:
- **Backend**: Django REST Framework API that integrates with Riot Games and Apex Legends APIs
- **Frontend**: Next.js application with Chakra UI for visualizing player statistics with interactive charts
- **Architecture**: Monorepo with separate backend and frontend directories

## Architecture

### Backend Structure (Django REST Framework)

**Core Framework** (Django 4.2.26, DRF 3.16.1):
- Settings: `backend/django/settings.py` - Full Django configuration with CORS, environment variables
- URLs: `backend/django/urls.py` - API endpoints for player search and match history
- Database: SQLite3 with migrations in `backend/migrations/`

**Django App** (`backend/`):
- `models.py`: Player, Match, PlayerMatchStats models
- `serializers.py`: DRF serializers for API responses
- `views.py`: API views for player lookup and match history
- `apps.py`: Django app configuration

**API Integration Layer** (`backend/auth/`):
- `riotAPI.py`: RiotAPIClient class with built-in rate limiting (429 handling) and retry logic
- `riotAuth.py`: Summoner name verification and Riot API authentication flow
- `apexAPI.py`: Apex Legends API integration via mozambiquehe.re bridge API

**Helper Functions** (`get_stats/`):
- `player_uiid.py`: Get player account by Riot ID
- `get_matches.py`: Fetch list of match IDs
- `get_ten_matches_data.py`: Fetch detailed match data

**Entry Points**:
- `manage.py`: Django management commands
- `main.py`: Legacy CLI-based entry point

### API Integration Details

**Riot Games API** (`RiotAPIClient`):
- Base URL: `https://na1.api.riotgames.com` (hardcoded to NA1 region)
- Authentication: X-Riot-Token header
- Built-in rate limit handling: Automatically retries on 429 with `Retry-After` header
- 3 retry attempts per request
- Rate limits: 20 requests/second, 100 requests/2 minutes
- API key regenerates every 24 hours

**Apex Legends API** (`apex_api_call`):
- Provider: mozambiquehe.re bridge API
- Endpoint: `https://api.mozambiquehe.re/bridge`
- Platform: PC (hardcoded)
- Rate limits: 1 request per 2 seconds (base), 2 requests per 2 seconds with Discord access

### Frontend Structure (Next.js + TypeScript)

**Tech Stack**:
- Next.js 15 with App Router
- TypeScript for type safety
- Chakra UI v3 for component library
- Recharts for data visualization
- Tailwind CSS for styling

**Project Structure** (`frontend/`):
- `app/`: Next.js app directory
  - `layout.tsx`: Root layout with Chakra UI provider
  - `page.tsx`: Main dashboard page
  - `providers.tsx`: Chakra UI provider setup
- `components/`: React components
  - `RiotIDInput.tsx`: Player search form
  - `StatsFilter.tsx`: Multi-select stat filter with auto-selected defaults
  - `SummaryCards.tsx`: Performance summary cards
  - `StatsLineChart.tsx`: Line chart for stat trends
  - `StatsBarChart.tsx`: Bar chart for K/D/A comparisons
- `lib/api.ts`: API client for backend integration
- `types/api.ts`: TypeScript types and stat filter constants

**API Endpoints Used**:
- `POST /api/players/search` - Look up player by Riot ID
- `GET /api/players/{puuid}/matches?limit=10` - Fetch match history

### API Endpoints (Django REST API)

**Available Endpoints**:
1. `POST /api/players/search`
   - Body: `{"game_name": "PlayerName", "tag_line": "NA1"}`
   - Returns: Player PUUID and basic info
   - Creates/updates Player in database

2. `GET /api/players/{puuid}/matches?limit=10`
   - Returns: Match history with detailed stats and summary
   - Fetches from Riot API and caches in database
   - Includes aggregated statistics (avg KDA, win rate, etc.)

### API Key Management

**Environment Variables** (stored in `.env`):
- `RIOT_API_KEY`: Riot Games development API key (24-hour expiration)
- `APEX_API_KEY`: Apex Legends mozambiquehe.re API key
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated CORS origins

**Security**: API keys are loaded using `python-decouple` from `.env` file (gitignored)

## Development Setup

### Backend Setup

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Riot API key and Apex API key
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start Django development server**:
   ```bash
   python manage.py runserver
   ```
   Server will run at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   # .env.local already configured for localhost:8000
   ```

4. **Start Next.js development server**:
   ```bash
   npm run dev
   ```
   Frontend will run at `http://localhost:3000`

### Full Stack Development

To run both backend and frontend simultaneously:

**Terminal 1 (Backend)**:
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Then visit `http://localhost:3000` to use the application.

## Key Dependencies

**Backend**:
- Django 4.2.26
- djangorestframework 3.16.1
- django-cors-headers 4.9.0
- python-decouple 3.8
- requests 2.32.5

**Frontend**:
- Next.js 15
- React 19
- TypeScript 5+
- Chakra UI v3
- Recharts 2.x
- Tailwind CSS

## Features

**Auto-Selected Stats** (displayed by default):
- Kills, Deaths, Assists, Wins

**Optional Stats** (user can select):
- Combat: Damage, Damage per minute, Multikills (doubles, triples, quadras, pentas), KDA
- Economy: Gold earned, Gold per minute, CS (minions killed)
- Vision: Vision score, Wards placed, Wards destroyed
- Performance: Kill participation percentage

**Visualizations**:
- Summary cards with aggregated stats (win rate, avg KDA, avg damage, etc.)
- Line chart showing stat trends across last 10 matches
- Bar chart comparing K/D/A per match (color-coded by win/loss)

## Current State & Implementation Notes

**Completed**:
- Full Django REST API with Player, Match, and PlayerMatchStats models
- Riot API integration with rate limiting and error handling
- Database caching of match data
- CORS configuration for local development
- Next.js frontend with TypeScript
- Chakra UI components for search, filtering, and visualization
- Recharts integration for interactive charts
- Responsive design for mobile and desktop

**Known Limitations**:
- Riot API development key expires every 24 hours (needs manual regeneration)
- Region hardcoded to NA1 for Riot API calls
- Platform hardcoded to PC for Apex API calls
- Match limit capped at 20 per request
- No user authentication or saved preferences
- No test suite implemented yet

**Database**:
- SQLite3 (suitable for development)
- Migrations tracked in `backend/migrations/`
- Data persisted across requests (no need to re-fetch from Riot API)
