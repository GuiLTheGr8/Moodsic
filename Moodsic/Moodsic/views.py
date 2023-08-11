# Create your views here.
from django.shortcuts import render
from transformers import pipeline
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import base64
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

def homepage(request):
    classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)

    if request.method == 'POST':
        
        # Recuperar texto digitado
        userInput = request.POST.get('user_input')

        # Análise sentimental
        textAnalysis = classifier(userInput)
        print(textAnalysis)
        print('')
        mood = getHighestMood(textAnalysis)
        print("Detected mood: " + mood)
        print('')

        # Obter palavras chave para pesquisa
        keywords = getKeywords(mood, userInput)

        # Autenticação Spotify
        clientId = os.getenv("CLIENT_ID")
        clientSecret = os.getenv("CLIENT_SECRET")
        auth_manager = SpotifyClientCredentials(client_id = clientId, client_secret = clientSecret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fazer a busca por playlists com as palavras-chaves
        results = sp.search(q=keywords, type='playlist', limit=20)

        # Extrair informações das playlists encontradas
        for playlist in results['playlists']['items']:
            prettyPlaylist = json.dumps(playlist, indent=2)
            print(prettyPlaylist)
            # print('ID da Playlist:', playlist['id'])
            # print('Número de Seguidores:', playlist['followers']['total'])
            print('')

    return render(request, 'Moodsic/index.html')

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
        keywords = "underground"

    # Essa função deve ser melhorada:
    # - mais keywords: possibilidades de palavras alternativas (ex: chance de "chill" e/ou "happy")
    # - ou pela busca de termos no userInput (ex: beach, work, traffic, study)
    # - também devemos implementar a possibilidade de keywords opostas (ex: pessoa está triste mas quer ouvir feliz)
    
    return keywords

def getHighestMood(textAnalysis):

    highestMoodScore = 0
    highestMood = ""

    for mood in textAnalysis[0]:
        if (mood['score'] > highestMoodScore):
            highestMoodScore = mood['score']
            highestMood = mood['label']

    return highestMood

def getSpotifyToken():

    clientId = os.getenv("CLIENT_ID")
    clientSecret = os.getenv("CLIENT_SECRET")

    authString = clientId + ":" + clientSecret
    authBytes = authString.encode("utf-8")
    