"use client";

import { useState } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Grid,
  Alert,
  Spinner,
  Button,
} from '@chakra-ui/react';
import { RiotIDInput } from '@/components/RiotIDInput';
import { StatsFilter } from '@/components/StatsFilter';
import { SummaryCards } from '@/components/SummaryCards';
import { StatsLineChart } from '@/components/StatsLineChart';
import { StatsBarChart } from '@/components/StatsBarChart';
import { api, APIError } from '@/lib/api';
import { PlayerMatchHistoryResponse, StatKey, DEFAULT_SELECTED_STATS } from '@/types/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playerData, setPlayerData] = useState<PlayerMatchHistoryResponse | null>(null);
  const [selectedStats, setSelectedStats] = useState<StatKey[]>(DEFAULT_SELECTED_STATS);

  const handleSearch = async (gameName: string, tagLine: string) => {
    setIsLoading(true);
    setError(null);
    setPlayerData(null);

    try {
      const data = await api.fetchPlayerStats(gameName, tagLine, 10);
      setPlayerData(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      console.error('Error fetching player data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setPlayerData(null);
    setError(null);
    setSelectedStats(DEFAULT_SELECTED_STATS);
  };

  return (
    <Box bg="gray.50" minH="100vh" py={8}>
      <Container maxW="container.xl">
        <VStack gap={8} align="stretch">
          {/* Header */}
          <Box textAlign="center">
            <Text fontSize="4xl" fontWeight="bold" color="gray.800" mb={2}>
              GameTrack
            </Text>
            <Text fontSize="lg" color="gray.600">
              Track and visualize your League of Legends statistics
            </Text>
          </Box>

          {/* Search Input */}
          <RiotIDInput onSubmit={handleSearch} isLoading={isLoading} />

          {/* Loading State */}
          {isLoading && (
            <Box textAlign="center" py={8}>
              <Spinner size="xl" color="blue.500" thickness="4px" mb={4} />
              <Text color="gray.600">
                Fetching player data from Riot API...
              </Text>
            </Box>
          )}

          {/* Error State */}
          {error && (
            <Alert.Root status="error">
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>Error</Alert.Title>
                <Alert.Description>{error}</Alert.Description>
              </Alert.Content>
            </Alert.Root>
          )}

          {/* Results */}
          {playerData && !isLoading && (
            <>
              {/* Player Info Header */}
              <Box
                p={6}
                borderRadius="lg"
                borderWidth="1px"
                borderColor="gray.200"
                bg="white"
                shadow="sm"
              >
                <HStack justify="space-between" align="center">
                  <VStack align="start" gap={1}>
                    <Text fontSize="2xl" fontWeight="bold" color="gray.800">
                      {playerData.player.game_name}#{playerData.player.tag_line}
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                      Showing last {playerData.total_matches} matches
                    </Text>
                  </VStack>
                  <Button onClick={handleReset} variant="outline" colorScheme="gray">
                    Search Another Player
                  </Button>
                </HStack>
              </Box>

              {/* Summary Cards */}
              <SummaryCards summary={playerData.summary} />

              {/* Stats and Charts Layout */}
              <Grid
                templateColumns={{ base: '1fr', lg: '300px 1fr' }}
                gap={6}
              >
                {/* Stats Filter (Sidebar on large screens) */}
                <Box>
                  <StatsFilter
                    selectedStats={selectedStats}
                    onChange={setSelectedStats}
                  />
                </Box>

                {/* Charts */}
                <VStack gap={6} align="stretch">
                  {/* Line Chart */}
                  <StatsLineChart
                    matches={playerData.matches}
                    selectedStats={selectedStats}
                  />

                  {/* Bar Chart */}
                  <StatsBarChart
                    matches={playerData.matches}
                    selectedStats={selectedStats}
                  />
                </VStack>
              </Grid>
            </>
          )}

          {/* Empty State */}
          {!playerData && !isLoading && !error && (
            <Box
              p={12}
              textAlign="center"
              borderRadius="lg"
              borderWidth="1px"
              borderColor="gray.200"
              bg="white"
            >
              <Text fontSize="xl" color="gray.600" mb={2}>
                Enter a Riot ID to get started
              </Text>
              <Text fontSize="sm" color="gray.500">
                Your stats and match history will appear here
              </Text>
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  );
}
