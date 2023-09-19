# Create your views here.
from datetime import datetime
from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from transformers import pipeline
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Moodsic, Playlist
from django.views.generic.list import ListView
from django.views.generic.base import View

def homepage(request):
    return render(request, 'Moodsic/index.html')

def searchPlaylist(request):
     if request.method == 'POST':
        
        # Recuperar texto digitado
        userInput = request.POST.get('user_input')

        # Recuperar escolha de oposto
        opposite = request.POST.get('opposite')
        
        load_dotenv()
        classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion', top_k = None)

        # Sentimental analysis
        textAnalysis = classifier(userInput)
        mood = getHighestMood(textAnalysis)
        print("Detected mood: " + mood)
        print('')

        # Obtain keywords for search
        keywords = getKeywords(mood, userInput, opposite)

        # Spotify auth
        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Search playlists with acquired keywords
        results = sp.search(q=keywords, type='playlist', limit=20)

        if results['playlists']['items']:
            playlist = random.choice(results['playlists']['items'])
        
        playlist_info = {}
        
        if playlist:
            playlist_info = {
                'title': playlist['name'],
                'description': playlist['description'],
                'owner': playlist['owner']['display_name'],
                'image': playlist['images'][0]['url'] if playlist['images'] else None,
                'link': playlist['external_urls']['spotify'],
            }

        context = {
            'search_date': datetime.now(),
            'user_input': userInput,
            'text_analysis': textAnalysis,
            'mood': mood,
            'playlist_info': playlist_info,
            'opposite': False,
            'error': True if len(playlist_info) == 0 else False,
        }

        return render(request, 'Moodsic/result.html', context)

def getHighestMood(textAnalysis):

    highestMoodScore = 0
    highestMood = ""

    for mood in textAnalysis[0]:
        if (mood['score'] > highestMoodScore):
            highestMoodScore = mood['score']
            highestMood = mood['label']

    return highestMood

def getKeywords(mood, userInput, opposite):

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


def result(request):
    
    if request.method == 'POST':
        print("POST received! (result)")
        userInput = request.POST.get('user_input')
        oppositeText = request.POST.get('opposite')
        opposite = True if oppositeText == "Yes" else False
        context = {
            'user_input': userInput,
            'opposite': opposite
        }
        return render(request, 'Moodsic/index.html')

@login_required
def save_results(request):
    print("POST received! (save results)")

    playlist_title = request.POST.get('playlist_title')
    playlist_description = request.POST.get('playlist_description')
    playlist_owner = request.POST.get('playlist_owner')
    playlist_link = request.POST.get('playlist_link')
    playlist_image = request.POST.get('playlist_image')

    typedText = request.POST.get('user_input')
    searchDate = request.POST.get('search_date')
    mood = request.POST.get('mood')
    opposite = request.POST.get('opposite')
    user = request.user

    playlist = Playlist(title = playlist_title, description = playlist_description, owner = playlist_owner, link = playlist_link, image = playlist_image)
    playlist.save()

    moodsic = Moodsic(user = user, playlist = playlist, mood = mood, typedText = typedText, searchDate = searchDate, opposite = opposite)
    moodsic.save()

    return HttpResponseRedirect('/')

class TimelineView(LoginRequiredMixin, ListView):
    model = Moodsic
    template_name = 'Moodsic/timeline.html'
    context_object_name = 'moodsics'
    success_url = reverse_lazy('timeline')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moodsics'] = context['moodsics'].filter(user = self.request.user)

        return context
    
class MoodsicDelete(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        moodsic = Moodsic.objects.get(pk=pk)
        context = { 'moodsic': moodsic }
        return render(request, 'Moodsic/moodsic-delete.html', context)

    def post(self, request, pk, *args, **kwargs):
        Moodsic.objects.filter(pk=pk).delete()
        return HttpResponseRedirect(reverse_lazy("timeline"))

def register(request):
    if request.method == 'POST':
        # create user
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
        else:
            context = {'form': form, }
        return render(request, 'Moodsic/register.html', context)
    else:
        # render form
        form = UserCreationForm()
    context = {'form': form, }
    return render(request, 'Moodsic/register.html', context)