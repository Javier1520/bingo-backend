# bingo/models.py
from django.contrib.auth.models import User
from django.db import models
import random
import threading
import time
from django.utils import timezone

class Game(models.Model):
    is_active = models.BooleanField(default=False)
    drawn_balls = models.JSONField(default=list)
    players = models.ManyToManyField(User, through='Player')
    start_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')

    def draw_ball(self):
        if len(self.drawn_balls) < 75:
            available_balls = set(range(1, 76)) - set(self.drawn_balls)
            new_ball = random.choice(list(available_balls))
            self.drawn_balls.append(new_ball)
            self.save()
            return new_ball
        return None

    def can_start(self):
        return self.players.count() >= 3

    def start_countdown(self):
        time.sleep(30)
        if not self.is_active and self.players.count() >= 3:
            self.is_active = True
            self.start_time = timezone.now()
            self.save()
            self.start_ball_drawing()

    def start_ball_drawing(self):
        while self.is_active and len(self.drawn_balls) < 75:
            time.sleep(5)
            new_ball = self.draw_ball()
            if not new_ball:
                self.is_active = False
                self.save()
                break

    def validate_bingo_card(self, player):
        card_numbers = [num for column in player.bingo_card.numbers.values() if column for num in column if num]
        return all(num in self.drawn_balls for num in card_numbers)

class BingoCard(models.Model):
    numbers = models.JSONField(unique=True)

    def generate_unique_card(self):
        while True:
            card = {
                'B': random.sample(range(1, 16), 5),
                'I': random.sample(range(16, 31), 5),
                'N': random.sample(range(31, 46), 5),
                'G': random.sample(range(46, 61), 5),
                'O': random.sample(range(61, 76), 5),
            }
            card['N'][2] = None
            if not BingoCard.objects.filter(numbers=card).exists():
                self.numbers = card
                self.save()
                break

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bingo_card = models.OneToOneField(BingoCard, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
