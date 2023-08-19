# Create your views here.
from django.shortcuts import render
from transformers import pipeline
from dotenv import load_dotenv
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

load_dotenv()

def homepage(request):
    classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=False)

    if request.method == 'POST':
        
        # Recuperar texto digitado
        userInput = request.POST.get('user_input')

        if (userInput == ""):
            return render(request, 'Moodsic/index.html')

        # Análise sentimental
        textAnalysis = classifier(userInput)
        mood = textAnalysis[0]['label']
        print("Detected mood: " + mood)
        print('')

        # Obter palavras chave para pesquisa
        keywords = getKeywords(mood, userInput)

        # Autenticação Spotify
        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fazer a busca por playlists com as palavras-chaves
        results = sp.search(q=keywords, type='playlist', limit=1, offset=random.randint(0,19))
        playlist = results['playlists']['items'][0]

        playlist_info = {}

        if playlist:
            playlist_info = {
                'title': playlist['name'],
                'image': playlist['images'][0]['url'] if playlist['images'] else None,
                'link': playlist['external_urls']['spotify'],
                'error': False,
            }
        else:
            playlist_info = {
                'title': 'error',
                'image': None,
                'link': playlist['external_urls']['spotify'],
                'error': True,
            }

        context = {
            'user_input': userInput,
            'text_analysis': textAnalysis,
            'mood': mood,
            'playlist_info': playlist_info
        }

        return render(request, 'Moodsic/result.html', context)

    return render(request, 'Moodsic/index.html')

def result(request, context):
    return render(request, 'Moodsic/result.html')

""" def getHighestMood(textAnalysis):

    highestMoodScore = 0
    highestMood = ""

    for mood in textAnalysis[0]:
        if (mood['score'] > highestMoodScore):
            highestMoodScore = mood['score']
            highestMood = mood['label']

    return highestMood """

def getKeywords(mood, userInput):

    keywords = ''
    
    if mood == "sadness":
        keywords = "sad"
    elif mood == "joy":
        keywords = "happy"
    elif mood == "love":
        keywords = "love"
    elif mood == "anger":
        keywords = "angry"
    elif mood == "fear":
        keywords = "horror"
    elif mood == "surprise":
        keywords = "surprise"

    # Essa função deve ser melhorada:
    # - mais keywords: possibilidades de palavras alternativas (ex: chance de "chill" e/ou "happy")
    # - ou pela busca de termos no userInput (ex: beach, work, traffic, study)
    # - também devemos implementar a possibilidade de keywords opostas (ex: pessoa está triste mas quer ouvir feliz)
    
    return keywords