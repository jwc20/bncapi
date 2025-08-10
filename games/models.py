# models.py
from django.db import models
from django.db.models import JSONField
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=128, blank=True)
    
    ########## TODO: deprecate, store them in game_state
    secret_code = models.CharField(max_length=4, blank=True)
    code_length = models.IntegerField(default=4, blank=True)
    num_of_colors = models.IntegerField(default=6, blank=True)
    num_of_guesses = models.IntegerField(default=10, blank=True)
    game_type = models.IntegerField(default=0)  # 0 = singleplayer, 1 = multiplayer, 2 =multiplayer (single board)
    ##########

    active_users = models.ManyToManyField(User, related_name="active_rooms", blank=True)
    game_state = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            next_id = Room.objects.count() + 1
            self.name = f"room_{next_id}"
        super().save(*args, **kwargs)

    def initialize_game(self):
        from bncpy.bnc.utils import get_random_number

        if not self.secret_code:
            self.secret_code = get_random_number(
                number=self.code_length, maximum=self.num_of_colors
            )

        self.game_state = {
            "guesses": [],
            "currentRow": 0,
            "gameOver": False,
            "gameWon": False,
            "remainingGuesses": self.num_of_guesses,
            "secretCode": None,  # Don't reveal until game over
            "players": [],
        }
        self.save()


class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content} [{self.timestamp}]"
