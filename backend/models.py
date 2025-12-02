from django.db import models
from django.utils import timezone


class Player(models.Model):
    """Stores Riot Games player information"""
    puuid = models.CharField(max_length=78, primary_key=True, help_text="Player Universal Unique Identifier")
    game_name = models.CharField(max_length=100, help_text="Riot ID game name")
    tag_line = models.CharField(max_length=10, help_text="Riot ID tag line")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'players'
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        indexes = [
            models.Index(fields=['game_name', 'tag_line']),
        ]

    def __str__(self):
        return f"{self.game_name}#{self.tag_line}"


class Match(models.Model):
    """Stores League of Legends match information"""
    match_id = models.CharField(max_length=50, primary_key=True, help_text="Match ID (e.g., NA1_5302453222)")
    game_creation = models.BigIntegerField(help_text="Unix timestamp when game was created")
    game_duration = models.IntegerField(help_text="Game duration in seconds")
    game_mode = models.CharField(max_length=50, help_text="Game mode (e.g., CLASSIC, ARAM)")
    game_type = models.CharField(max_length=50, help_text="Game type (e.g., MATCHED_GAME)")

    raw_data = models.JSONField(help_text="Full match data from Riot API", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['-game_creation']
        indexes = [
            models.Index(fields=['-game_creation']),
        ]

    def __str__(self):
        return f"Match {self.match_id}"

    @property
    def game_datetime(self):
        """Convert Unix timestamp to datetime"""
        return timezone.datetime.fromtimestamp(self.game_creation / 1000, tz=timezone.utc)


class PlayerMatchStats(models.Model):
    """Stores individual player statistics for a specific match"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_stats')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_stats')

    # Core stats
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    win = models.BooleanField(default=False)

    # Champion info
    champion_id = models.IntegerField()
    champion_name = models.CharField(max_length=50)
    champ_level = models.IntegerField(default=1)

    # Combat stats
    double_kills = models.IntegerField(default=0)
    triple_kills = models.IntegerField(default=0)
    quadra_kills = models.IntegerField(default=0)
    penta_kills = models.IntegerField(default=0)
    total_damage_dealt_to_champions = models.IntegerField(default=0)

    # Economy stats
    gold_earned = models.IntegerField(default=0)
    total_minions_killed = models.IntegerField(default=0)

    # Vision stats
    vision_score = models.IntegerField(default=0)
    wards_placed = models.IntegerField(default=0)
    wards_killed = models.IntegerField(default=0)

    # Calculated metrics
    kda = models.FloatField(null=True, blank=True, help_text="KDA ratio from challenges")
    kill_participation = models.FloatField(null=True, blank=True, help_text="Kill participation percentage")
    damage_per_minute = models.FloatField(null=True, blank=True)
    gold_per_minute = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'player_match_stats'
        verbose_name = 'Player Match Stats'
        verbose_name_plural = 'Player Match Stats'
        unique_together = [['player', 'match']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['player', '-created_at']),
            models.Index(fields=['win']),
        ]

    def __str__(self):
        return f"{self.player} - {self.match.match_id} ({self.kills}/{self.deaths}/{self.assists})"

    def save(self, *args, **kwargs):
        """Calculate KDA on save"""
        if self.deaths == 0:
            self.kda = float(self.kills + self.assists)
        else:
            self.kda = round((self.kills + self.assists) / self.deaths, 2)
        super().save(*args, **kwargs)
