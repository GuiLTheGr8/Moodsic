# Create your views here.
from datetime import datetime
from typing import Any
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
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

load_dotenv()

def homepage(request):
    return render(request, 'Moodsic/index.html')

def searchPlaylist(request):
     if request.method == 'POST':
        
        # Recuperar texto digitado
        userInput = request.POST.get('user_input')

        if userInput.strip() == '':
            return HttpResponseRedirect('/')

        # Recuperar escolha de oposto
        opposite = request.POST.get('opposite')
        if opposite != "Yes":
            opposite = "No"
    
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
            'opposite': opposite,
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
    if opposite == "Yes":
        if mood == "sadness":
            keywordList = ["happy","joy", "good vibes", "happiness", "positive", "healing"]
            keywords = random.choice(keywordList)
        elif mood == "joy":
            keywordList = ["sad","sadness", "melancholic", "melancholy", "cry", "depress"]
            keywords = random.choice(keywordList)
        elif mood == "love":
            keywordList = ["loner", "lonely", "neutral", "alone", "loneliness", "breakup"]
            keywords = random.choice(keywordList)
        elif mood == "anger":
            keywordList = ["calm", "chill", "dream", "peace", "relax", "stress relief"]
            keywords = random.choice(keywordList)
        elif mood == "fear":
            keywordList = ["calm", "chill", "dream", "peace", "relax", "stress relief"]
            keywords = random.choice(keywordList)
        elif mood == "surprise":
            keywordList = ["hit", "pop", "top", "neutral", "famous"]
            keywords = random.choice(keywordList)
    else:
        if mood == "sadness":
            keywordList = ["sad","sadness", "melancholic", "melancholy", "cry", "depress"]
            keywords = random.choice(keywordList)
        elif mood == "joy":
            keywordList = ["happy","joy", "joyful", "good vibes", "happiness", "positive"]
            keywords = random.choice(keywordList)
        elif mood == "love":
            keywordList = ["love","lovebirds", "valentine", "soulmate", "romantic"]
            keywords = random.choice(keywordList)
        elif mood == "anger":
            keywordList = ["angry","anger", "heavy", "pissed off", "rage"]
            keywords = random.choice(keywordList)
        elif mood == "fear":
            keywordList = ["fear","horror", "terror", "dark", "scary"]
            keywords = random.choice(keywordList)
        elif mood == "surprise":
            keywordList = ["hipster", "surprising", "underground", "less known", "hidden gem"]
            keywords = random.choice(keywordList)

    # Essa função deve ser melhorada:
    # - Pela busca de termos no userInput (ex: beach, work, traffic, study)
    
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
    oppositeText = request.POST.get('opposite')
    opposite = True if oppositeText and oppositeText == "Yes" else False
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

    def get_queryset(self):
        return Moodsic.objects.order_by('-searchDate')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moodsics'] = context['moodsics'].filter(user = self.request.user)

        angerCount = Moodsic.objects.filter(mood='anger', user = self.request.user).count()
        fearCount = Moodsic.objects.filter(mood='fear', user = self.request.user).count()
        joyCount = Moodsic.objects.filter(mood='joy', user = self.request.user).count()
        loveCount = Moodsic.objects.filter(mood='love', user = self.request.user).count()
        sadnessCount = Moodsic.objects.filter(mood='sadness', user = self.request.user).count()
        surpriseCount = Moodsic.objects.filter(mood='surprise', user = self.request.user).count()

        data_points = [
            { "label": "anger",  "y": angerCount },
            { "label": "fear", "y": fearCount },
            { "label": "joy", "y": joyCount },
            { "label": "love",  "y": loveCount },
            { "label": "sadness",  "y": sadnessCount },
            { "label": "surprise",  "y": surpriseCount }
        ]
        context['data_points'] = data_points

        search_input = self.request.GET.get('search-area') or ''

        if search_input:
            context['moodsics'] = context['moodsics'].filter(typedText__icontains=search_input)

        context['search_input'] = search_input

        return context
    
class MoodsicDelete(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        moodsic = get_object_or_404(Moodsic, pk=pk)
        if moodsic.user == self.request.user:
            context = { 'moodsic': moodsic }
            return render(request, 'Moodsic/moodsic-delete.html', context)
        else:
            raise Http404("You don't have permission to delete this Moodsic.")

    def post(self, request, pk, *args, **kwargs):
        moodsic = Moodsic.objects.get(pk=pk)
        if moodsic.user == self.request.user:
            Moodsic.objects.filter(pk=pk).delete()
            return HttpResponseRedirect(reverse_lazy("timeline"))
        else:
            raise Http404("You don't have permission to delete this Moodsic.")
        
class MoodsicDetails(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        moodsic = get_object_or_404(Moodsic, pk=pk)
        if moodsic.user == self.request.user:
            context = { 'moodsic': moodsic }
            return render(request, 'Moodsic/moodsic-details.html', context)
        else:
            raise Http404("You don't have permission to view this Moodsic.")

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