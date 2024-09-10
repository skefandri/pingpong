import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.players = []
        self.matchups = []
        self.winners = []
        self.losers = []
        self.current_stage = "semi_finals"  # Track the current stage of the tournament
        self.current_match = 0
        self.current_game_loop_task = None  # Keep track of the current game loop task
        self.game_state = {
            'paddle1Y': (400 - 75) / 2,
            'paddle2Y': (400 - 75) / 2,
            'ballX': 800 / 2,
            'ballY': 400 / 2,
            'ballSpeedX': 2,
            'ballSpeedY': 2,
            'score1': 0,
            'score2': 0,
            'gameOver': False,
            'winner': ''
        }

    async def disconnect(self, close_code):
        if self.current_game_loop_task:
            self.current_game_loop_task.cancel()
        await self.close()
        print(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"data: {data}")
        action = data.get('action')

        if action == 'submit_players':
            self.players = data.get('players')
            random.shuffle(self.players)
            self.matchups = [
                (self.players[0], self.players[1]),
                (self.players[2], self.players[3])
            ]
            await self.send(text_data=json.dumps({
                'status': 'success',
                'matchups': self.matchups,
            }))

        elif action == 'start_tournament':
            self.current_stage = "semi_finals"
            self.current_match = 0
            self.winners = []
            self.losers = []
            await self.start_next_match()

        elif action == 'paddle_movement':
            self.handle_paddle_movement(data.get('player'), data.get('direction'))

    def handle_paddle_movement(self, player, direction):
        # Slow down the paddle movement by reducing the step size
        step_size = 2  # Adjust this value to control the paddle speed
        if player == 'player1':
            print(f"player: {player} directiom: {direction}")
            if direction == 'up':
                self.game_state['paddle1Y'] = max(self.game_state['paddle1Y'] - step_size, 0)
            elif direction == 'down':
                self.game_state['paddle1Y'] = min(self.game_state['paddle1Y'] + step_size, 400 - 75)
        elif player == 'player2':
            if direction == 'up':
                self.game_state['paddle2Y'] = max(self.game_state['paddle2Y'] - step_size, 0)
            elif direction == 'down':
                self.game_state['paddle2Y'] = min(self.game_state['paddle2Y'] + step_size, 400 - 75)

    async def start_next_match(self):
        if self.current_game_loop_task:
            self.current_game_loop_task.cancel()
        
        if self.current_stage == "semi_finals":
            if self.current_match < len(self.matchups):
                player1, player2 = self.matchups[self.current_match]
                self.reset_game_state(player1, player2)
                await self.send(text_data=json.dumps({
                    'status': 'start_match',
                    'player1': player1,
                    'player2': player2,
                }))
                self.current_game_loop_task = asyncio.create_task(self.run_game_loop())
            else:
                # After semi-finals, set up the 3rd place and final matches
                self.current_stage = "finals"
                self.current_match = 0
                self.matchups = [
                    (self.losers[0], self.losers[1]),  # Third-place match
                    (self.winners[0], self.winners[1])  # Final match
                ]
                await self.start_next_match()
        elif self.current_stage == "finals":
            if self.current_match < len(self.matchups):
                player1, player2 = self.matchups[self.current_match]
                self.reset_game_state(player1, player2)
                await self.send(text_data=json.dumps({
                    'status': 'start_match',
                    'player1': player1,
                    'player2': player2,
                }))
                self.current_game_loop_task = asyncio.create_task(self.run_game_loop())
            else:
                tournament_winner = self.winners[-1]
                await self.send(text_data=json.dumps({
                    'status': 'tournament_complete',
                    'winner': tournament_winner,
                    'semi_final_results': self.matchups[:2],
                    'third_place_result': self.matchups[0],
                    'final_result': self.matchups[1],
                }))
    async def run_game_loop(self):
        while not self.game_state['gameOver']:
            self.update_ball_position()
            await self.send_game_state()
            await asyncio.sleep(0.02)

    def update_ball_position(self):
        if not self.game_state['gameOver']:
            # Update ball position
            self.game_state['ballX'] += self.game_state['ballSpeedX']
            self.game_state['ballY'] += self.game_state['ballSpeedY']

            # Ball collision with top and bottom walls
            if self.game_state['ballY'] - 10 < 0 or self.game_state['ballY'] + 10 > 400:
                self.game_state['ballSpeedY'] = -self.game_state['ballSpeedY']

            # Ball collision with paddles
            if self.game_state['ballX'] - 10 <= 10:  # Left paddle (Player 1)
                if self.game_state['paddle1Y'] < self.game_state['ballY'] < self.game_state['paddle1Y'] + 75:
                    self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
                    deltaY = self.game_state['ballY'] - (self.game_state['paddle1Y'] + 75 / 2)
                    self.game_state['ballSpeedY'] += deltaY * 0.09  # Slight variation in speed based on hit point
                else:
                    self.game_state['score2'] += 1
                    self.reset_ball()

            elif self.game_state['ballX'] + 10 >= 800 - 10:  # Right paddle (Player 2)
                if self.game_state['paddle2Y'] < self.game_state['ballY'] < self.game_state['paddle2Y'] + 75:
                    self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
                    deltaY = self.game_state['ballY'] - (self.game_state['paddle2Y'] + 75 / 2)
                    self.game_state['ballSpeedY'] += deltaY * 0.09  # Slight variation in speed based on hit point
                else:
                    self.game_state['score1'] += 1
                    self.reset_ball()

            # Check if someone won
            if self.game_state['score1'] >= 1:
                self.end_match(self.game_state['player1'])

            elif self.game_state['score2'] >= 1:
                self.end_match(self.game_state['player2'])

    def end_match(self, winner):
        self.game_state['gameOver'] = True
        self.game_state['winner'] = winner

        if self.current_stage == "semi_finals":
            self.winners.append(winner)
            loser = self.matchups[self.current_match][0] if winner != self.matchups[self.current_match][0] else self.matchups[self.current_match][1]
            self.losers.append(loser)

        elif self.current_stage == "finals":
            if self.current_match == 0:  # Third place match
                self.losers.append(winner)
            else:  # Final match
                self.winners.append(winner)

        self.current_match += 1
        asyncio.create_task(self.start_next_match())

    def reset_ball(self):
        self.game_state['ballX'] = 800 / 2
        self.game_state['ballY'] = 400 / 2
        self.game_state['ballSpeedX'] = random.choice([-2, 2])
        self.game_state['ballSpeedY'] = random.choice([-2, 2])
        self.game_state['paddle1Y'] = (400 - 75) / 2
        self.game_state['paddle2Y'] = (400 - 75) / 2

    def reset_game_state(self, player1, player2):
        self.game_state = {
            'paddle1Y': (400 - 75) / 2,
            'paddle2Y': (400 - 75) / 2,
            'ballX': 800 / 2,
            'ballY': 400 / 2,
            'ballSpeedX': random.choice([-2, 2]),
            'ballSpeedY': random.choice([-2, 2]),
            'score1': 0,
            'score2': 0,
            'gameOver': False,
            'winner': '',
            'player1': player1,
            'player2': player2
        }

    async def send_game_state(self):
        await self.send(text_data=json.dumps(self.game_state))
