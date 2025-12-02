"use client";

import { Box, Text } from '@chakra-ui/react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { PlayerMatchStats, StatKey } from '@/types/api';

interface StatsLineChartProps {
  matches: PlayerMatchStats[];
  selectedStats: StatKey[];
}

const STAT_COLORS: Record<string, string> = {
  kills: '#10b981',
  deaths: '#ef4444',
  assists: '#3b82f6',
  kda: '#8b5cf6',
  total_damage_dealt_to_champions: '#f59e0b',
  damage_per_minute: '#f97316',
  gold_earned: '#fbbf24',
  gold_per_minute: '#fb923c',
  total_minions_killed: '#a855f7',
  vision_score: '#06b6d4',
  wards_placed: '#0891b2',
  wards_killed: '#0e7490',
  kill_participation: '#ec4899',
  double_kills: '#84cc16',
  triple_kills: '#65a30d',
  quadra_kills: '#16a34a',
  penta_kills: '#059669',
};

const STAT_LABELS: Record<string, string> = {
  kills: 'Kills',
  deaths: 'Deaths',
  assists: 'Assists',
  kda: 'KDA',
  total_damage_dealt_to_champions: 'Damage',
  damage_per_minute: 'DPM',
  gold_earned: 'Gold',
  gold_per_minute: 'GPM',
  total_minions_killed: 'CS',
  vision_score: 'Vision',
  wards_placed: 'Wards',
  wards_killed: 'Wards Killed',
  kill_participation: 'KP%',
  double_kills: 'Doubles',
  triple_kills: 'Triples',
  quadra_kills: 'Quadras',
  penta_kills: 'Pentas',
};

export function StatsLineChart({ matches, selectedStats }: StatsLineChartProps) {
  // Prepare data for the chart (reverse to show oldest to newest)
  const chartData = matches
    .slice()
    .reverse()
    .map((match, index) => {
      const data: Record<string, string | number> = {
        match: `Match ${index + 1}`,
        champion: match.champion_name,
      };

      selectedStats.forEach((stat) => {
        // Handle win as 1/0 for charting
        if (stat === 'win') {
          data[stat] = match[stat] ? 1 : 0;
        } else {
          const value = match[stat as keyof PlayerMatchStats];
          data[stat] = typeof value === 'number' ? value : 0;
        }
      });

      return data;
    });

  // Filter out stats that shouldn't be on line chart (win is better as bar chart)
  const statsToDisplay = selectedStats.filter((stat) => stat !== 'win');

  if (statsToDisplay.length === 0) {
    return (
      <Box
        p={6}
        borderRadius="lg"
        borderWidth="1px"
        borderColor="gray.200"
        bg="white"
        shadow="sm"
      >
        <Text color="gray.500" textAlign="center">
          Select stats to display the trend chart
        </Text>
      </Box>
    );
  }

  return (
    <Box
      p={6}
      borderRadius="lg"
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      shadow="sm"
    >
      <Text fontSize="xl" fontWeight="bold" color="gray.700" mb={4}>
        Stats Trend (Last {matches.length} Matches)
      </Text>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="match" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '14px' }} />

          {statsToDisplay.map((stat) => (
            <Line
              key={stat}
              type="monotone"
              dataKey={stat}
              name={STAT_LABELS[stat] || stat}
              stroke={STAT_COLORS[stat] || '#6b7280'}
              strokeWidth={2}
              dot={{ fill: STAT_COLORS[stat] || '#6b7280', r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}
