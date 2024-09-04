












# import json
# import random
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

# class TournamentConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.players = []
#         self.matchups = []
#         self.winners = []
#         self.losers = []
#         self.current_match = 0
#         self.game_state = {
#             'paddle1Y': (400 - 75) / 2,
#             'paddle2Y': (400 - 75) / 2,
#             'ballX': 800 / 2,
#             'ballY': 400 / 2,
#             'ballSpeedX': 2,  # Set a reasonable speed for the ball
#             'ballSpeedY': 2,
#             'score1': 0,
#             'score2': 0,
#             'gameOver': False,
#             'winner': ''
#         }

#     async def disconnect(self, close_code):
#         await self.close()
#         print(f"WebSocket connection closed with code: {close_code}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         print(f"Received data: {data}")
#         action = data.get('action')
#         print("================================")
#         print(f"action: {action}")
#         if action == 'submit_players':
#             self.players = data.get('players')
#             print(f"players before radom.shuffle: {self.players}")
#             random.shuffle(self.players)
#             print(f"players After radom.shuffle: {self.players}")
#             self.matchups = [
#                 (self.players[0], self.players[1]),
#                 (self.players[2], self.players[3])
#             ]
#             await self.send(text_data=json.dumps({
#                 'status': 'success',
#                 'matchups': self.matchups,
#             }))

#         elif action == 'start_tournament':
#             self.current_match = 0
#             self.winners = []
#             await self.start_next_match()

#         elif action == 'paddle_movement':
#             self.handle_paddle_movement(data.get('player'), data.get('direction'))

#     def handle_paddle_movement(self, player, direction):
#         if player == 'player1':
#             if direction == 'up':
#                 self.game_state['paddle1Y'] = max(self.game_state['paddle1Y'] - 8, 0)
#             elif direction == 'down':
#                 self.game_state['paddle1Y'] = min(self.game_state['paddle1Y'] + 8, 400 - 75)
#         elif player == 'player2':
#             if direction == 'up':
#                 self.game_state['paddle2Y'] = max(self.game_state['paddle2Y'] - 8, 0)
#             elif direction == 'down':
#                 self.game_state['paddle2Y'] = min(self.game_state['paddle2Y'] + 8, 400 - 75)

#     async def start_next_match(self):
#         if self.current_match < len(self.matchups):
#             player1, player2 = self.matchups[self.current_match]
#             self.reset_game_state(player1, player2)
#             await self.send(text_data=json.dumps({
#                 'status': 'start_match',
#                 'player1': player1,
#                 'player2': player2,
#             }))
#             asyncio.create_task(self.run_game_loop())
#         else:
#             tournament_winner = self.determine_tournament_winner()
#             await self.send(text_data=json.dumps({
#                 'status': 'tournament_complete',
#                 'winner': tournament_winner,
#             }))

#     async def run_game_loop(self):
#         while not self.game_state['gameOver']:
#             self.update_ball_position()
#             await self.send_game_state()
#             await asyncio.sleep(0.02)  # Controls the speed of the game loop (20 ms per frame)

#     def determine_tournament_winner(self):
#         # The final match is between the winners of the two semi-final matches
#         final_match_winner = self.winners[-1]  # The winner of the final match
#         return final_match_winner

#     def update_ball_position(self):
#         if not self.game_state['gameOver']:
#             # Update ball position
#             self.game_state['ballX'] += self.game_state['ballSpeedX']
#             self.game_state['ballY'] += self.game_state['ballSpeedY']

#             # Ball collision with top and bottom walls
#             if self.game_state['ballY'] - 10 < 0 or self.game_state['ballY'] + 10 > 400:
#                 self.game_state['ballSpeedY'] = -self.game_state['ballSpeedY']

#             # Ball collision with paddles
#             if self.game_state['ballX'] - 10 <= 10:  # Left paddle (Player 1)
#                 if self.game_state['paddle1Y'] < self.game_state['ballY'] < self.game_state['paddle1Y'] + 75:
#                     self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
#                     deltaY = self.game_state['ballY'] - (self.game_state['paddle1Y'] + 75 / 2)
#                     self.game_state['ballSpeedY'] += deltaY * 0.02  # Slight variation in speed based on hit point
#                 else:
#                     self.game_state['score2'] += 1
#                     self.reset_ball()

#             elif self.game_state['ballX'] + 10 >= 800 - 10:  # Right paddle (Player 2)
#                 if self.game_state['paddle2Y'] < self.game_state['ballY'] < self.game_state['paddle2Y'] + 75:
#                     self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
#                     deltaY = self.game_state['ballY'] - (self.game_state['paddle2Y'] + 75 / 2)
#                     self.game_state['ballSpeedY'] += deltaY * 0.02  # Slight variation in speed based on hit point
#                 else:
#                     self.game_state['score1'] += 1
#                     self.reset_ball()

#             # Check if someone won
#             if self.game_state['score1'] >= 1:
#                 self.end_match(self.game_state['player1'])

#             elif self.game_state['score2'] >= 1:
#                 self.end_match(self.game_state['player2'])

#     def end_match(self, winner):
#         self.game_state['gameOver'] = True
#         self.game_state['winner'] = winner
#         self.winners.append(winner)
#         self.current_match += 1
#         asyncio.create_task(self.start_next_match())

#     def reset_ball(self):
#         self.game_state['ballX'] = 800 / 2
#         self.game_state['ballY'] = 400 / 2
#         self.game_state['ballSpeedX'] = random.choice([-2, 2])
#         self.game_state['ballSpeedY'] = random.choice([-2, 2])

#     def reset_game_state(self, player1, player2):
#         self.game_state = {
#             'paddle1Y': (400 - 75) / 2,
#             'paddle2Y': (400 - 75) / 2,
#             'ballX': 800 / 2,
#             'ballY': 400 / 2,
#             'ballSpeedX': random.choice([-2, 2]),
#             'ballSpeedY': random.choice([-2, 2]),
#             'score1': 0,
#             'score2': 0,
#             'gameOver': False,
#             'winner': '',
#             'player1': player1,
#             'player2': player2
#         }

#     async def send_game_state(self):
#         await self.send(text_data=json.dumps(self.game_state))











# import json
# import random
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

# class TournamentConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.players = []
#         self.matchups = []
#         self.winners = []
#         self.losers = []
#         self.current_match = 0
#         self.stage = "semi-finals"  # Track the stage of the tournament
#         self.game_state = {
#             'paddle1Y': (400 - 75) / 2,
#             'paddle2Y': (400 - 75) / 2,
#             'ballX': 700 / 2,
#             'ballY': 400 / 2,
#             'ballSpeedX': random.choice([-2, 2]),  # Random initial direction
#             'ballSpeedY': random.choice([-2, 2]),
#             'score1': 0,
#             'score2': 0,
#             'gameOver': False,
#             'winner': ''
#         }

#     async def disconnect(self, close_code):
#         # Clean up resources if needed
#         print(f"WebSocket disconnected with code {close_code}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         action = data.get('action')

#         if action == 'submit_players':
#             self.players = data.get('players')
#             random.shuffle(self.players)
#             self.matchups = [
#                 (self.players[0], self.players[1]),
#                 (self.players[2], self.players[3])
#             ]
#             await self.send(text_data=json.dumps({
#                 'status': 'success',
#                 'matchups': self.matchups,
#             }))

#         elif action == 'start_tournament':
#             self.current_match = 0
#             self.winners = []
#             self.losers = []
#             self.stage = "semi-finals"
#             await self.start_next_match()

#         elif action == 'paddle_movement':
#             self.handle_paddle_movement(data.get('player'), data.get('direction'))

#     def handle_paddle_movement(self, player, direction):
#         if player == 'player1':
#             if direction == 'up':
#                 self.game_state['paddle1Y'] = max(self.game_state['paddle1Y'] - 8, 0)
#             elif direction == 'down':
#                 self.game_state['paddle1Y'] = min(self.game_state['paddle1Y'] + 8, 400 - 75)
#         elif player == 'player2':
#             if direction == 'up':
#                 self.game_state['paddle2Y'] = max(self.game_state['paddle2Y'] - 8, 0)
#             elif direction == 'down':
#                 self.game_state['paddle2Y'] = min(self.game_state['paddle2Y'] + 8, 400 - 75)

#     async def start_next_match(self):
#         if self.stage == "semi-finals" and self.current_match < len(self.matchups):
#             player1, player2 = self.matchups[self.current_match]
#             self.reset_game_state(player1, player2)
#             await self.send(text_data=json.dumps({
#                 'status': 'start_match',
#                 'player1': player1,
#                 'player2': player2,
#             }))
#             asyncio.create_task(self.run_game_loop())

#         elif self.stage == "classification":
#             player1, player2 = self.losers
#             self.reset_game_state(player1, player2)
#             await self.send(text_data=json.dumps({
#                 'status': 'start_match',
#                 'player1': player1,
#                 'player2': player2,
#             }))
#             asyncio.create_task(self.run_game_loop())

#         elif self.stage == "final":
#             player1, player2 = self.winners
#             self.reset_game_state(player1, player2)
#             await self.send(text_data=json.dumps({
#                 'status': 'start_match',
#                 'player1': player1,
#                 'player2': player2,
#             }))
#             asyncio.create_task(self.run_game_loop())

#         elif self.stage == "tournament_complete":
#             tournament_winner = self.determine_tournament_winner()
#             await self.send(text_data=json.dumps({
#                 'status': 'tournament_complete',
#                 'winner': tournament_winner,
#             }))

#     async def run_game_loop(self):
#         while not self.game_state['gameOver']:
#             self.update_ball_position()
#             await self.send_game_state()
#             await asyncio.sleep(0.02)  # 50 frames per second

#     def determine_tournament_winner(self):
#         return self.winners[-1]  # The winner of the final match

#     def update_ball_position(self):
#         if not self.game_state['gameOver']:
#             self.game_state['ballX'] += self.game_state['ballSpeedX']
#             self.game_state['ballY'] += self.game_state['ballSpeedY']

#             if self.game_state['ballY'] + 10 > 400 or self.game_state['ballY'] - 10 < 0:
#                 self.game_state['ballSpeedY'] = -self.game_state['ballSpeedY']

#             if self.game_state['ballX'] - 10 < 10:
#                 if self.game_state['paddle1Y'] < self.game_state['ballY'] < self.game_state['paddle1Y'] + 75:
#                     self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
#                     deltaY = self.game_state['ballY'] - (self.game_state['paddle1Y'] + 75 / 2)
#                     self.game_state['ballSpeedY'] += deltaY * 0.02
#                 else:
#                     self.game_state['score2'] += 1
#                     self.end_match(self.game_state['player2'])
#                     self.reset_ball()

#             elif self.game_state['ballX'] + 10 > 700 - 10:
#                 if self.game_state['paddle2Y'] < self.game_state['ballY'] < self.game_state['paddle2Y'] + 75:
#                     self.game_state['ballSpeedX'] = -self.game_state['ballSpeedX']
#                     deltaY = self.game_state['ballY'] - (self.game_state['paddle2Y'] + 75 / 2)
#                     self.game_state['ballSpeedY'] += deltaY * 0.02
#                 else:
#                     self.game_state['score1'] += 1
#                     self.end_match(self.game_state['player1'])
#                     self.reset_ball()

#             if self.game_state['score1'] >= 1:
#                 self.game_state['gameOver'] = True
#                 self.game_state['winner'] = self.game_state['player1']
#                 self.winners.append(self.game_state['player1'])
#                 self.losers.append(self.game_state['player2'])
#                 self.current_match += 1
#                 asyncio.create_task(self.handle_match_completion())

#             elif self.game_state['score2'] >= 1:
#                 self.game_state['gameOver'] = True
#                 self.game_state['winner'] = self.game_state['player2']
#                 self.winners.append(self.game_state['player2'])
#                 self.losers.append(self.game_state['player1'])
#                 self.current_match += 1
#                 asyncio.create_task(self.handle_match_completion())
#     def end_match(self, winner):
#         self.game_state['gameOver'] = True
#         self.game_state['winner'] = winner
#         self.winners.append(winner)
#         self.current_match += 1
#         asyncio.create_task(self.start_next_match())
#     async def handle_match_completion(self):
#         if self.stage == "semi-finals" and self.current_match >= len(self.matchups):
#             self.stage = "classification"
#             self.current_match = 0
#         elif self.stage == "classification":
#             self.stage = "final"
#         elif self.stage == "final":
#             self.stage = "tournament_complete"
#         await self.start_next_match()

#     def reset_ball(self):
#         self.game_state['ballX'] = 700 / 2
#         self.game_state['ballY'] = 400 / 2
#         self.game_state['ballSpeedX'] = random.choice([-4, 4])
#         self.game_state['ballSpeedY'] = random.choice([-4, 4])

#     def reset_game_state(self, player1, player2):
#         self.game_state['score1'] = 0
#         self.game_state['score2'] = 0
#         self.game_state['gameOver'] = False
#         self.game_state['winner'] = ''
#         self.game_state['ballX'] = 700 / 2
#         self.game_state['ballY'] = 400 / 2
#         self.game_state['ballSpeedX'] = random.choice([-4, 4])
#         self.game_state['ballSpeedY'] = random.choice([-4, 4])
#         self.game_state['player1'] = player1
#         self.game_state['player2'] = player2

#     async def send_game_state(self):
#         await self.send(text_data=json.dumps(self.game_state))
