from django.contrib.auth import get_user_model

from django.db import models

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=128, blank=True)
    # online = models.ManyToManyField(to=User, blank=True)
    secret_code = models.CharField(max_length=6, blank=True)
    code_length = models.IntegerField(default=4, blank=True)
    num_of_colors = models.IntegerField(default=6, blank=True)
    num_of_guesses = models.IntegerField(default=10, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.name:
            next_id = Room.objects.count() + 1
            self.name = f"room_{next_id}"

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content} [{self.timestamp}]"
