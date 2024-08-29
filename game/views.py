from django.shortcuts import render

# Create your views here.
def tournaments(request):
    return render(request, "game/tournament.html")

from django.shortcuts import render
from django.http import JsonResponse
from .models import Tournament
import json

def create_tournament(request):
    if request.method == 'POST':
        players = json.loads(request.body).get('players')
        if len(players) != 4:
            return JsonResponse({'error': 'You must submit exactly 4 players.'}, status=400)
        
        tournament = Tournament.objects.create(players=json.dumps(players))
        return JsonResponse({'tournament_id': tournament.id})
    
    return render(request, 'game/tournament.html')
