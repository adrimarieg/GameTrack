"use client";

import { useState } from 'react';
import { Box, Input, Button, HStack, VStack, Text } from '@chakra-ui/react';

interface RiotIDInputProps {
  onSubmit: (gameName: string, tagLine: string) => void;
  isLoading?: boolean;
}

export function RiotIDInput({ onSubmit, isLoading = false }: RiotIDInputProps) {
  const [gameName, setGameName] = useState('');
  const [tagLine, setTagLine] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedGameName = gameName.trim();
    const trimmedTagLine = tagLine.trim().replace('#', ''); // Remove # if user included it

    if (trimmedGameName && trimmedTagLine) {
      onSubmit(trimmedGameName, trimmedTagLine);
    }
  };

  return (
    <Box
      as="form"
      onSubmit={handleSubmit}
      p={6}
      borderRadius="lg"
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      shadow="sm"
    >
      <VStack gap={4} align="stretch">
        <Text fontSize="xl" fontWeight="bold" color="gray.700">
          Enter Riot ID
        </Text>

        <HStack gap={3}>
          <Input
            placeholder="Game Name"
            value={gameName}
            onChange={(e) => setGameName(e.target.value)}
            size="lg"
            required
            disabled={isLoading}
            bg="gray.50"
            borderColor="gray.300"
            color="gray.800"
            _focus={{
              borderColor: 'blue.500',
              bg: 'white',
            }}
          />

          <Text fontSize="2xl" color="gray.400" fontWeight="bold">
            #
          </Text>

          <Input
            placeholder="Tag Line"
            value={tagLine}
            onChange={(e) => setTagLine(e.target.value)}
            size="lg"
            required
            disabled={isLoading}
            maxLength={10}
            bg="gray.50"
            borderColor="gray.300"
            color="gray.800"
            _focus={{
              borderColor: 'blue.500',
              bg: 'white',
            }}
          />
        </HStack>

        <Button
          type="submit"
          colorScheme="blue"
          size="lg"
          isDisabled={!gameName.trim() || !tagLine.trim() || isLoading}
          loading={isLoading}
          loadingText="Searching..."
        >
          Search Player
        </Button>

        <Text fontSize="sm" color="gray.500">
          Example: PlayerName#NA1
        </Text>
      </VStack>
    </Box>
  );
}
