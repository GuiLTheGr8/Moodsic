# Create your views here.
from django.shortcuts import render
from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def homepage(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        prediction = classifier(user_input)
        print(prediction)
        
        return render(request, 'Moodsic/index.html')

    classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)
    return render(request, 'Moodsic/index.html')