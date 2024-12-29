import asyncio
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BingoCard, Player, Game
from .consumers import GameConsumer
import threading

class RegisterToGameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        game, created = Game.objects.get_or_create(is_active=False, winner=None)

        if game.players.count() >= 10:
            return Response({"error": "Game is full"}, status=status.HTTP_400_BAD_REQUEST)

        if Player.objects.filter(user=user, game__is_active=True).exists():
            return Response({"error": "User is already registered for an active game"}, status=status.HTTP_400_BAD_REQUEST)


        card = BingoCard()
        card.generate_unique_card()

        try:
            player = Player.objects.create(user=user, bingo_card=card, game=game)
            game.players.add(user)

            if game.players.count() == 1:
                threading.Thread(target=self.check_timeout, args=(game,)).start()

            if game.can_start() and not game.is_active:
                threading.Thread(target=game.start_countdown).start()

            return Response({"player": player.user.username, "card": player.bingo_card.numbers}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {"error": "User is already registered with a bingo card for this game"},
                status=status.HTTP_400_BAD_REQUEST)

    def check_timeout(self, game):
        """Deletes the game if it doesn't reach 2 players within 60 seconds."""
        import time

        time.sleep(60)
        if game.players.count() < 2 and not game.is_active:
            # Notify the single player (if any)
            player = Player.objects.filter(game=game).first()
            if player:
                print(f"Notifying user {player.user.username}: Game canceled due to insufficient players.")

            game.delete()


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

        if game.validate_bingo_card(player):
            game.winner = user
            game.is_active = False
            game.save()
            asyncio.run(GameConsumer.send_to_all({
                    'type': 'game.finish',
                    'message': {'state': 'finished'}
                }))
            asyncio.run(GameConsumer.disconnect_all())
            return Response({"message": f"{user.username} wins the game!"}, status=status.HTTP_200_OK)
        else:
            player.delete()
            if game.players.count() == 0:
                game.is_active = False
                asyncio.run(GameConsumer.disconnect_all())
                game.delete()
            return Response({"error": "Invalid claim, you are disqualified"}, status=status.HTTP_403_FORBIDDEN)

class GetBingoCardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).last()

        if not player:
            return Response({"error": "User is not part of an active game"}, status=status.HTTP_400_BAD_REQUEST)
        card = {key: player.bingo_card.numbers[key] for key in ['B', 'I', 'N', 'G', 'O']}
        return Response({"card": card}, status=status.HTTP_200_OK)
