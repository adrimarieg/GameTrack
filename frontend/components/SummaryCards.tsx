"use client";

import { SimpleGrid, Box, VStack, Text, HStack, Badge } from '@chakra-ui/react';
import { Summary } from '@/types/api';

interface SummaryCardsProps {
  summary: Summary;
}

interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  colorScheme?: 'blue' | 'green' | 'red' | 'purple' | 'orange';
}

function StatCard({ label, value, subValue, colorScheme = 'blue' }: StatCardProps) {
  return (
    <Box
      p={5}
      borderRadius="lg"
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      shadow="sm"
      _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
      transition="all 0.2s"
    >
      <VStack gap={2} align="stretch">
        <Text fontSize="sm" color="gray.600" fontWeight="medium">
          {label}
        </Text>
        <HStack justify="space-between" align="baseline">
          <Text fontSize="3xl" fontWeight="bold" color={`${colorScheme}.600`}>
            {value}
          </Text>
          {subValue && (
            <Badge colorScheme={colorScheme} fontSize="sm" px={2} py={1} borderRadius="md">
              {subValue}
            </Badge>
          )}
        </HStack>
      </VStack>
    </Box>
  );
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <Box>
      <Text fontSize="2xl" fontWeight="bold" color="gray.700" mb={4}>
        Performance Summary
      </Text>

      <SimpleGrid columns={{ base: 2, md: 3, lg: 4 }} gap={4}>
        <StatCard
          label="Total Matches"
          value={summary.total_matches}
          colorScheme="blue"
        />

        <StatCard
          label="Win Rate"
          value={`${summary.win_rate}%`}
          subValue={`${summary.wins}W ${summary.losses}L`}
          colorScheme={summary.win_rate >= 50 ? 'green' : 'red'}
        />

        <StatCard
          label="Average KDA"
          value={summary.avg_kda}
          subValue={`${summary.avg_kills}/${summary.avg_deaths}/${summary.avg_assists}`}
          colorScheme="purple"
        />

        <StatCard
          label="Avg Kills"
          value={summary.avg_kills}
          colorScheme="green"
        />

        <StatCard
          label="Avg Deaths"
          value={summary.avg_deaths}
          colorScheme="red"
        />

        <StatCard
          label="Avg Assists"
          value={summary.avg_assists}
          colorScheme="blue"
        />

        <StatCard
          label="Avg Damage"
          value={(summary.avg_damage || 0).toLocaleString()}
          colorScheme="orange"
        />

        <StatCard
          label="Avg Gold"
          value={(summary.avg_gold || 0).toLocaleString()}
          colorScheme="orange"
        />

        <StatCard
          label="Avg CS"
          value={summary.avg_cs}
          colorScheme="purple"
        />

        <StatCard
          label="Avg Vision Score"
          value={summary.avg_vision_score}
          colorScheme="blue"
        />
      </SimpleGrid>
    </Box>
  );
}
