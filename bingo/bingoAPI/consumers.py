import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

class GameConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # Maintain a set of connected WebSocket clients

    async def connect(self):
        try:
            # Parse token from query params
            query_params = parse_qs(self.scope['query_string'].decode())
            token = query_params.get('token', [None])[0]
            print(f"\n\nToken received: {token}\n\n")

            # Authenticate user with the token
            self.user = await self.authenticate_user(token)
            if not self.user:
                print("\n\nUser authentication failed\n\n")
                await self.close()
                return

            # Fetch active game
            self.game = await self.get_active_game()
            if not self.game:
                print("\n\nNo active game found\n\n")
                await self.close()
                return

            # Add client to the set of connected clients
            self.connected_clients.add(self)

            # Accept the WebSocket connection
            await self.accept()
            print("\n\nWebSocket connection accepted\n\n")
            await self.send(text_data=json.dumps({
                'type': 'game.ball',
                'message': {'ball': 'B2'}
            }))

        except Exception as e:
            print(f"\n\nException during connect: {e}\n\n")
            await self.close()

    async def disconnect(self, close_code):
        # Remove the client from the set of connected clients
        self.connected_clients.discard(self)
        print(f"\n\nWebSocket disconnected with close code: {close_code}\n\n")

    @classmethod
    async def send_to_all(cls, message):
        """
        Broadcast a message to all connected WebSocket clients.
        """
        print(f"Broadcasting message to {len(cls.connected_clients)} clients: {message}")
        for client in cls.connected_clients:
            try:
                await client.send(text_data=json.dumps(message))
            except Exception as e:
                print(f"Error sending message to client: {e}")

    @database_sync_to_async
    def authenticate_user(self, token):
        from rest_framework.authtoken.models import Token
        try:
            print("\n\nValidating token\n\n")
            return Token.objects.get(key=token).user
        except Token.DoesNotExist:
            print("\n\nInvalid token\n\n")
            return None

    @database_sync_to_async
    def get_active_game(self):
        from .models import Game
        try:
            return Game.objects.get(is_active=False, winner=None)
        except Game.DoesNotExist:
            print("\n\nNo active game found\n\n")
            return None
