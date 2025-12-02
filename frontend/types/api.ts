// TypeScript types for GameTrack API responses

export interface Player {
  puuid: string;
  game_name: string;
  tag_line: string;
  created_at: string;
  updated_at: string;
}

export interface PlayerMatchStats {
  // Match info
  match_id: string;
  game_datetime: string;
  game_duration: number;
  game_mode: string;

  // Core stats
  kills: number;
  deaths: number;
  assists: number;
  win: boolean;
  kda: number;

  // Champion info
  champion_id: number;
  champion_name: string;
  champ_level: number;

  // Combat stats
  double_kills: number;
  triple_kills: number;
  quadra_kills: number;
  penta_kills: number;
  total_damage_dealt_to_champions: number;
  damage_per_minute: number | null;

  // Economy stats
  gold_earned: number;
  gold_per_minute: number | null;
  total_minions_killed: number;

  // Vision stats
  vision_score: number;
  wards_placed: number;
  wards_killed: number;

  // Performance metrics
  kill_participation: number | null;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface Summary {
  total_matches: number;
  wins: number;
  losses: number;
  win_rate: number;
  avg_kills: number;
  avg_deaths: number;
  avg_assists: number;
  avg_kda: number;
  avg_damage: number;
  avg_gold: number;
  avg_cs: number;
  avg_vision_score: number;
}

export interface PlayerMatchHistoryResponse {
  player: Player;
  matches: PlayerMatchStats[];
  total_matches: number;
  summary: Summary;
}

export interface PlayerLookupRequest {
  game_name: string;
  tag_line: string;
}

export interface PlayerLookupResponse {
  player: Player;
  created: boolean;
}

// Stats that can be filtered
export type StatKey =
  | 'kills'
  | 'deaths'
  | 'assists'
  | 'win'
  | 'kda'
  | 'total_damage_dealt_to_champions'
  | 'damage_per_minute'
  | 'gold_earned'
  | 'gold_per_minute'
  | 'total_minions_killed'
  | 'vision_score'
  | 'wards_placed'
  | 'wards_killed'
  | 'kill_participation'
  | 'double_kills'
  | 'triple_kills'
  | 'quadra_kills'
  | 'penta_kills';

export interface StatFilter {
  key: StatKey;
  label: string;
  category: 'core' | 'combat' | 'economy' | 'vision' | 'performance';
}

// Available stat filters
export const STAT_FILTERS: StatFilter[] = [
  // Core stats (auto-selected)
  { key: 'kills', label: 'Kills', category: 'core' },
  { key: 'deaths', label: 'Deaths', category: 'core' },
  { key: 'assists', label: 'Assists', category: 'core' },
  { key: 'win', label: 'Wins', category: 'core' },

  // Combat stats
  { key: 'kda', label: 'KDA', category: 'performance' },
  { key: 'total_damage_dealt_to_champions', label: 'Damage to Champions', category: 'combat' },
  { key: 'damage_per_minute', label: 'Damage per Minute', category: 'combat' },
  { key: 'double_kills', label: 'Double Kills', category: 'combat' },
  { key: 'triple_kills', label: 'Triple Kills', category: 'combat' },
  { key: 'quadra_kills', label: 'Quadra Kills', category: 'combat' },
  { key: 'penta_kills', label: 'Penta Kills', category: 'combat' },

  // Economy stats
  { key: 'gold_earned', label: 'Gold Earned', category: 'economy' },
  { key: 'gold_per_minute', label: 'Gold per Minute', category: 'economy' },
  { key: 'total_minions_killed', label: 'CS (Minions)', category: 'economy' },

  // Vision stats
  { key: 'vision_score', label: 'Vision Score', category: 'vision' },
  { key: 'wards_placed', label: 'Wards Placed', category: 'vision' },
  { key: 'wards_killed', label: 'Wards Destroyed', category: 'vision' },

  // Performance metrics
  { key: 'kill_participation', label: 'Kill Participation %', category: 'performance' },
];

// Default auto-selected stats
export const DEFAULT_SELECTED_STATS: StatKey[] = ['kills', 'deaths', 'assists', 'win'];
