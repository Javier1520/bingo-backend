from django.contrib.auth.models import User
from django.db import models
import random
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
        return self.players.count() >= 2

    def start_countdown(self):
        time.sleep(30)
        self.refresh_from_db()
        if not self.is_active:

            self.is_active = True
            self.start_time = timezone.now()
            self.save()
            self.start_ball_drawing()

    def start_ball_drawing(self):
        while self.is_active:
            time.sleep(5)
            self.refresh_from_db()
            new_ball = self.draw_ball()
            print(new_ball)
            if not new_ball:
                self.is_active = False
                self.save()
                break

    def validate_bingo_card(self, player):
        return player.bingo_card.is_winner(self.drawn_balls)

    def get_bingo_letter(self, number):
        if 1 <= number <= 15:
            return 'B'
        elif 16 <= number <= 30:
            return 'I'
        elif 31 <= number <= 45:
            return 'N'
        elif 46 <= number <= 60:
            return 'G'
        elif 61 <= number <= 75:
            return 'O'


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

    def is_winner(self, drawn_balls):
        numbers = self.numbers
        drawn_balls = set(drawn_balls)
        columns = ['B', 'I', 'N', 'G', 'O']

        rows = [set() for _ in range(5)]
        cols = [set() for _ in range(5)]
        diagonals = [set(), set()]
        corners = set()
        marked_count = 0
        total_cells = 0

        for i, col in enumerate(columns):
            for j, num in enumerate(numbers[col]):
                total_cells += 1

                # Skip free space
                if num is None:
                    marked_count += 1
                    rows[j].add('FREE')
                    cols[i].add('FREE')
                    if i == j:
                        diagonals[0].add('FREE')
                    if i + j == 4:
                        diagonals[1].add('FREE')
                    continue

                if num in drawn_balls:
                    marked_count += 1
                    rows[j].add(num)
                    cols[i].add(num)

                    if i == j:
                        diagonals[0].add(num)
                    if i + j == 4:
                        diagonals[1].add(num)

                    if (i in {0, 4}) and (j in {0, 4}):
                        corners.add(num)

        return any([
            any(len(row) == 5 for row in rows),        # Complete row
            any(len(col) == 5 for col in cols),        # Complete column
            any(len(diag) == 5 for diag in diagonals), # Complete diagonal
            len(corners) == 4,                         # Four corners
            marked_count == total_cells                # Full card
        ])

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bingo_card = models.OneToOneField(BingoCard, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'game']
