# GameTrack Frontend

A Next.js frontend for visualizing League of Legends player statistics with interactive charts and filters.

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Chakra UI v3** - Component library
- **Recharts** - Chart visualization library
- **Tailwind CSS** - Utility-first CSS

## Features

- Search players by Riot ID (GameName#TagLine)
- View comprehensive match history (last 10 matches)
- Interactive stat filtering
  - Auto-selected: Kills, Deaths, Assists, Wins
  - Combat stats: Damage, multikills, KDA
  - Economy stats: Gold, CS
  - Vision stats: Wards, vision score
  - Performance metrics: Kill participation
- Multiple chart visualizations:
  - Line charts for stat trends over time
  - Bar charts for per-match K/D/A comparison
  - Summary cards with aggregated statistics
- Real-time API integration with Django backend

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Django backend running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with Chakra UI provider
│   ├── page.tsx             # Main dashboard page
│   ├── providers.tsx        # Chakra UI provider setup
│   └── globals.css          # Global styles
├── components/
│   ├── RiotIDInput.tsx      # Player search form
│   ├── StatsFilter.tsx      # Multi-select stat filter
│   ├── SummaryCards.tsx     # Performance summary cards
│   ├── StatsLineChart.tsx   # Line chart for trends
│   └── StatsBarChart.tsx    # Bar chart for comparisons
├── lib/
│   └── api.ts               # API integration layer
├── types/
│   └── api.ts               # TypeScript types and constants
└── .env.local               # Environment variables (not committed)
```

## API Integration

The frontend communicates with the Django backend via REST API:

- `POST /api/players/search` - Look up player by Riot ID
- `GET /api/players/{puuid}/matches?limit=10` - Fetch match history

See `lib/api.ts` for API client implementation.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API base URL (default: `http://localhost:8000`)

## Development Notes

- The app uses Chakra UI v3 with the new `defaultSystem` theme
- Charts are rendered using Recharts with responsive containers
- All API calls include proper error handling and loading states
- TypeScript types are auto-generated from API responses

## Contributing

When adding new features:

1. Add types to `types/api.ts`
2. Update API client in `lib/api.ts`
3. Create/update components in `components/`
4. Integrate in `app/page.tsx`
