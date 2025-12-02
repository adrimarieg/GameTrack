"use client";

import { Box, Text } from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { PlayerMatchStats, StatKey } from '@/types/api';

interface StatsBarChartProps {
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

export function StatsBarChart({ matches, selectedStats }: StatsBarChartProps) {
  // Prepare data for the chart (reverse to show oldest to newest)
  const chartData = matches
    .slice()
    .reverse()
    .map((match, index) => {
      const data: Record<string, string | number | boolean> = {
        match: `M${index + 1}`,
        fullMatch: `Match ${index + 1}`,
        champion: match.champion_name,
        win: match.win,
      };

      selectedStats.forEach((stat) => {
        if (stat === 'win') {
          data[stat] = match[stat] ? 1 : 0;
        } else {
          const value = match[stat as keyof PlayerMatchStats];
          data[stat] = typeof value === 'number' ? value : 0;
        }
      });

      return data;
    });

  // For bar chart, show KDA comparison
  const kdaData = matches
    .slice()
    .reverse()
    .map((match, index) => ({
      match: `M${index + 1}`,
      fullMatch: `Match ${index + 1}`,
      champion: match.champion_name,
      Kills: match.kills,
      Deaths: match.deaths,
      Assists: match.assists,
      win: match.win,
    }));

  if (selectedStats.length === 0) {
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
          Select stats to display the comparison chart
        </Text>
      </Box>
    );
  }

  // Show KDA comparison if K/D/A are in selected stats
  const showKDA =
    selectedStats.includes('kills') ||
    selectedStats.includes('deaths') ||
    selectedStats.includes('assists');

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
        Per-Match Comparison (Last {matches.length} Matches)
      </Text>

      {showKDA && (
        <Box mb={6}>
          <Text fontSize="md" fontWeight="semibold" color="gray.600" mb={3}>
            K/D/A Breakdown
          </Text>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={kdaData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="match" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <Box
                        p={3}
                        bg="white"
                        borderWidth="1px"
                        borderColor="gray.200"
                        borderRadius="md"
                        shadow="md"
                      >
                        <Text fontWeight="bold" mb={1}>
                          {data.fullMatch}
                        </Text>
                        <Text fontSize="sm" color="gray.600" mb={2}>
                          {data.champion} - {data.win ? 'Victory' : 'Defeat'}
                        </Text>
                        {payload.map((entry: any) => (
                          <Text key={entry.name} fontSize="sm" color={entry.color}>
                            {entry.name}: {entry.value}
                          </Text>
                        ))}
                      </Box>
                    );
                  }
                  return null;
                }}
              />
              <Legend wrapperStyle={{ fontSize: '14px' }} />

              <Bar dataKey="Kills" fill={STAT_COLORS.kills}>
                {kdaData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.win ? STAT_COLORS.kills : '#9ca3af'}
                  />
                ))}
              </Bar>
              <Bar dataKey="Deaths" fill={STAT_COLORS.deaths}>
                {kdaData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.win ? STAT_COLORS.deaths : '#9ca3af'}
                  />
                ))}
              </Bar>
              <Bar dataKey="Assists" fill={STAT_COLORS.assists}>
                {kdaData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.win ? STAT_COLORS.assists : '#9ca3af'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Box>
  );
}
