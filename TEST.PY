import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Tournament

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'submit_players':
            players = data.get('players', [])
            if len(players) != 4:
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': 'Exactly 4 players are required.'
                }))
                return

            # Shuffle and create matchups
            random.shuffle(players)
            matchups = [
                {'match_id': 1, 'player1': players[0], 'player2': players[1], 'winner': None},
                {'match_id': 2, 'player1': players[2], 'player2': players[3], 'winner': None},
            ]

            # Save the tournament with players and matchups
            tournament = await sync_to_async(Tournament.objects.create)(
                name="Ping Pong Championship",
                players=json.dumps(players),
                matches=json.dumps(matchups)
            )

            await self.send(text_data=json.dumps({
                'status': 'success',
                'tournament_id': tournament.id,
                'matchups': matchups
            }))

        elif action == 'report_result':
            match_id = data.get('match_id')
            winner = data.get('winner')
            tournament_id = data.get('tournament_id')

            # Update the tournament with the winner of the match
            response = await self.update_match_result(tournament_id, match_id, winner)
            await self.send(text_data=json.dumps(response))

    @sync_to_async
    def update_match_result(self, tournament_id, match_id, winner):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            matches = json.loads(tournament.matches)

            # Update the match with the winner
            for match in matches:
                if match['match_id'] == match_id:
                    match['winner'] = winner
                    break

            remaining_players = [match['winner'] for match in matches if match['winner'] is not None]

            # If only one player remains, declare them as the tournament winner
            if len(remaining_players) == 2:
                final_match = {
                    'match_id': 3,
                    'player1': remaining_players[0],
                    'player2': remaining_players[1],
                    'winner': None
                }
                matches.append(final_match)
                tournament.matches = json.dumps(matches)
                tournament.save()

                return {
                    'status': 'success',
                    'next_match': final_match,
                    'matchups': matches
                }

            if len(remaining_players) == 1:
                tournament.winner = remaining_players[0]
                tournament.save()

                return {
                    'status': 'success',
                    'winner': remaining_players[0],
                    'message': 'Tournament complete!'
                }

            # Save the updated matches back to the tournament
            tournament.matches = json.dumps(matches)
            tournament.save()

            return {
                'status': 'success',
                'message': 'Match result updated.',
                'next_match': None,
                'matchups': matches
            }
        except Tournament.DoesNotExist:
            return {'status': 'error', 'message': 'Tournament not found.'}
