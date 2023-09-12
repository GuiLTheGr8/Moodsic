from django import forms

from django.db.models import fields
from django import forms
from Moodsic.models import *

class PlaylistModel2Form(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = '__all__'

class MoodsicModel2Form(forms.ModelForm):
    class Meta:
        model = Moodsic
        fields = '__all__'