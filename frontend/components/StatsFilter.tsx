"use client";

import { Box, VStack, HStack, Text, Badge, CheckboxGroup } from '@chakra-ui/react';
import { Checkbox } from '@chakra-ui/react';
import { STAT_FILTERS, StatKey, DEFAULT_SELECTED_STATS } from '@/types/api';

interface StatsFilterProps {
  selectedStats: StatKey[];
  onChange: (stats: StatKey[]) => void;
}

export function StatsFilter({ selectedStats, onChange }: StatsFilterProps) {
  // Group stats by category
  const statsByCategory = STAT_FILTERS.reduce((acc, stat) => {
    if (!acc[stat.category]) {
      acc[stat.category] = [];
    }
    acc[stat.category].push(stat);
    return acc;
  }, {} as Record<string, typeof STAT_FILTERS>);

  const categoryLabels = {
    core: 'Core Stats',
    combat: 'Combat Stats',
    economy: 'Economy Stats',
    vision: 'Vision Stats',
    performance: 'Performance Metrics',
  };

  const handleCheckboxChange = (values: string[]) => {
    onChange(values as StatKey[]);
  };

  return (
    <Box
      p={6}
      borderRadius="lg"
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      shadow="sm"
    >
      <VStack gap={5} align="stretch">
        <HStack justify="space-between" align="center">
          <Text fontSize="xl" fontWeight="bold" color="gray.700">
            Select Stats to Display
          </Text>
          <Badge colorScheme="blue" fontSize="sm" px={3} py={1} borderRadius="full">
            {selectedStats.length} selected
          </Badge>
        </HStack>

        <CheckboxGroup value={selectedStats} onChange={handleCheckboxChange}>
          <VStack gap={4} align="stretch">
            {Object.entries(statsByCategory).map(([category, stats]) => (
              <Box key={category}>
                <Text
                  fontSize="sm"
                  fontWeight="semibold"
                  color="gray.600"
                  textTransform="uppercase"
                  mb={2}
                >
                  {categoryLabels[category as keyof typeof categoryLabels]}
                </Text>

                <VStack gap={2} align="stretch" pl={2}>
                  {stats.map((stat) => {
                    const isDefault = DEFAULT_SELECTED_STATS.includes(stat.key);
                    return (
                      <Checkbox.Root key={stat.key} value={stat.key}>
                        <Checkbox.HiddenInput />
                        <Checkbox.Control>
                          <Checkbox.Indicator />
                        </Checkbox.Control>
                        <Checkbox.Label>
                          <HStack gap={2}>
                            <Text fontSize="sm">{stat.label}</Text>
                            {isDefault && (
                              <Badge
                                colorScheme="green"
                                fontSize="xs"
                                px={2}
                                py={0.5}
                                borderRadius="full"
                              >
                                Auto
                              </Badge>
                            )}
                          </HStack>
                        </Checkbox.Label>
                      </Checkbox.Root>
                    );
                  })}
                </VStack>
              </Box>
            ))}
          </VStack>
        </CheckboxGroup>
      </VStack>
    </Box>
  );
}
