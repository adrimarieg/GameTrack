from rest_framework import serializers
from .models import Player, Match, PlayerMatchStats


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""

    class Meta:
        model = Player
        fields = ['puuid', 'game_name', 'tag_line', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for Match model"""
    game_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'game_creation', 'game_datetime', 'game_duration',
            'game_mode', 'game_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PlayerMatchStatsSerializer(serializers.ModelSerializer):
    """Serializer for PlayerMatchStats model"""
    match_id = serializers.CharField(source='match.match_id', read_only=True)
    game_datetime = serializers.DateTimeField(source='match.game_datetime', read_only=True)
    game_duration = serializers.IntegerField(source='match.game_duration', read_only=True)
    game_mode = serializers.CharField(source='match.game_mode', read_only=True)

    class Meta:
        model = PlayerMatchStats
        fields = [
            # Match info
            'match_id', 'game_datetime', 'game_duration', 'game_mode',

            # Core stats
            'kills', 'deaths', 'assists', 'win', 'kda',

            # Champion info
            'champion_id', 'champion_name', 'champ_level',

            # Combat stats
            'double_kills', 'triple_kills', 'quadra_kills', 'penta_kills',
            'total_damage_dealt_to_champions', 'damage_per_minute',

            # Economy stats
            'gold_earned', 'gold_per_minute', 'total_minions_killed',

            # Vision stats
            'vision_score', 'wards_placed', 'wards_killed',

            # Performance metrics
            'kill_participation',

            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'kda']


class PlayerMatchHistorySerializer(serializers.Serializer):
    """Serializer for player match history with all stats"""
    player = PlayerSerializer(read_only=True)
    matches = PlayerMatchStatsSerializer(many=True, read_only=True)
    total_matches = serializers.IntegerField(read_only=True)

    # Summary statistics
    summary = serializers.DictField(read_only=True)


class PlayerLookupSerializer(serializers.Serializer):
    """Serializer for player lookup by Riot ID"""
    game_name = serializers.CharField(max_length=100, required=True, help_text="Riot ID game name (e.g., 'Player')")
    tag_line = serializers.CharField(max_length=10, required=True, help_text="Riot ID tag line (e.g., 'NA1')")

    def validate_game_name(self, value):
        """Validate game name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Game name cannot be empty")
        return value.strip()

    def validate_tag_line(self, value):
        """Validate tag line format"""
        if not value.strip():
            raise serializers.ValidationError("Tag line cannot be empty")
        # Remove '#' if user included it
        return value.strip().lstrip('#')
