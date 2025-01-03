import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class GameConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # Maintain a set of connected WebSocket clients

    async def connect(self):
        try:
            # Accept the WebSocket connection
            await self.accept()
            print("\n\nWebSocket connection accepted\n\n")

            # Wait for the token after the connection is established
            # The token validation logic will be inside the `receive` method

        except Exception as e:
            print(f"\n\nException during connect: {e}\n\n")
            await self.close()

    async def receive(self, text_data):
        """
        Handles receiving a message over WebSocket and token validation.
        """
        try:
            # Decode the received data
            text_data_json = json.loads(text_data)
            token = text_data_json.get('token')

            # Token validation
            if not token:
                print("Token not found in the received data.")
                await self.close(code=4004)  # Close if no token is provided
                return  # Early return to avoid calling async functions

            print(f"Received token: {token}")

            # Authenticate user with the token
            self.user = await self.authenticate_user(token)  # Use await to call async method
            if not self.user:
                print("\n\nUser authentication failed\n\n")
                await self.close(code=4003)  # Close with authentication error code
                return  # Early return to avoid further processing

            # Fetch active game
            self.game = await self.get_active_game()  # Use await to call async method
            if not self.game:
                print("\n\nNo active game found\n\n")
                await self.close()
                return  # Early return to avoid further processing

            # Add client to the set of connected clients
            self.connected_clients.add(self)

            # Notify all clients about the total players
            await self.send_to_all({
                'type': 'game.total_players',
                'message': {'total_players': len(self.connected_clients)}
            })

            # Handle any other messages (optional)
            message = text_data_json.get('message')
            if message:
                print(f"Received message: {message}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            await self.close(code=4004)  # Close on error decoding JSON

        except Exception as e:
            print(f"Error processing received message: {e}")
            await self.close(code=4005)  # Close on general error


    async def disconnect(self, close_code):
        self.connected_clients.discard(self)
        print(f"\n\nWebSocket disconnected with close code: {close_code}\n\n")

    @classmethod
    async def disconnect_all(cls):
        """
        Disconnect all currently connected WebSocket clients.
        """
        print(f"\n\nDisconnecting all {len(cls.connected_clients)} clients.\n\n")
        for client in list(cls.connected_clients):  # Create a list copy to avoid modification during iteration
            try:
                await client.close()
            except Exception as e:
                print(f"Error disconnecting client: {e}")
        cls.connected_clients.clear()

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
