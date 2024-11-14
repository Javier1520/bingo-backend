# bingo/views.py
import time
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import BingoCard, Player, Game
import threading

class RegisterToGameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        game, created = Game.objects.get_or_create(is_active=False)

        if game.players.count() >= 10:
            return Response({"error": "Game is full"}, status=status.HTTP_400_BAD_REQUEST)

        if Player.objects.filter(user=user).exists():
            return Response({"error": "User is already registered for a game"}, status=status.HTTP_400_BAD_REQUEST)

        card = BingoCard()
        card.generate_unique_card()

        player = Player.objects.create(user=user, bingo_card=card, game=game)
        game.players.add(user)

        if game.can_start() and not game.is_active:
            threading.Thread(target=game.start_countdown).start()

        return Response({"player": player.user.username, "card": player.bingo_card.numbers}, status=status.HTTP_201_CREATED)


class LatestBallView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        game = Game.objects.filter(is_active=True).first()
        if not game or not game.drawn_balls:
            return Response({"message": "No balls drawn yet"}, status=status.HTTP_200_OK)

        last_ball = game.drawn_balls[-1]
        return Response({"latest_ball": last_ball}, status=status.HTTP_200_OK)

class ClaimWinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        game = Game.objects.filter(is_active=True).first()

        if not game:
            return Response({"error": "No active game"}, status=status.HTTP_400_BAD_REQUEST)

        player = Player.objects.filter(user=user, game=game).first()
        if not player:
            return Response({"error": "Player not registered in the game"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the player's bingo card
        if game.validate_bingo_card(player):
            game.winner = user
            game.is_active = False
            game.save()
            return Response({"message": f"{user.username} wins the game!"}, status=status.HTTP_200_OK)
        else:
            # Disqualify the player
            player.delete()
            return Response({"error": "Invalid claim, you are disqualified"}, status=status.HTTP_403_FORBIDDEN)
